from time import sleep, time
from threading import Thread, Event
from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import ctypes, sys
from ctypes import wintypes
import win32api
import win32con
import os   

# This is needed to get the correct mouse position for different DPI settings
ctypes.windll.user32.SetProcessDPIAware()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

user32 = ctypes.WinDLL('user32', use_last_error=True)

# TODO:
# - make sure all the keys can be recorded.

class Macro:
    def __init__(self):

        ''' Core Macro Variables '''
        self.inputs = [] # Inputs that the macro will execute, in the form of strings
        self.replays = [] # Replay functions for the inputs

        ''' State Variables '''
        self.recording = False
        self.executing = False
        self.preparing = False
        self.state_listener_active = False
        self.appending = False
        self.pause = False
        self.is_paused = False
        self.is_admin = is_admin() # Admin needed to block input

        ''' Configuration Variables '''
        self.macro_repeat_delay = 1 # delay between each repeat of the macro
        self.record_delays = False
        self._end_recording_key = Key.esc # Key to end a recording, default is esc
        self._end_prep_key = Key.esc # Key to end the prep time, default is esc
        self._terminate_macro_key = Key.esc # Key to terminate the macro, default is esc
        self.prep_time = 0 # Time to wait before recording starts
        self.click_uses_coords = False # mouse will click at the coordinates recorded instead of just a click
        self.move_delay = 0.01 # delay between moving the mouse and clicking, only used if click_uses_coords is True
        self.block_input_when_executing = False # Only possible if admin, USE WITH CAUTION, as even terminate macro key will be blocked
        self.keep_initial_position = False # macro will reset the mouse to where it was at the start of recording
        self.use_absolute_coords = True # mouse will move to the absolute coordinates recorded instead of relative to the current position
                                         # !!!This will make it incompatiple with first person games, but will make movements more accurate
        self.keep_initial_delay = False 

        ''' Controllers '''
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

        ''' Listeners '''
        self.start_state_listener()


    ''' Input recording '''

    def record_basic_input(self):
        ''' Record basic input such as key presses and mouse clicks, ignoring mouse movements. '''
        # We don't want the end recording key to work here
        self.end_recording_key = None

        self.record_delays = False
        self.inputs = []
        threshold = 0
        if self.keep_initial_position and not self.appending:
            threshold = 1  # Keep initial position adds an input to the start
            
        # Don't record key releases or mouse movements
        self.start_recording(kb_release=False, mouse_move=False)
        while self.recording:
            sleep(0.01)
            if len(self.inputs) > threshold:
                self.end_recording()
        self.inputs = self.inputs[:threshold + 1]  # Keep first threshold+1 items

        # Reset the end recording key
        self.end_recording_key = Key.esc
        
    def record_sequence(self, record_movements=False):
        ''' Records a sequence of basic inputs, ignoring mouse movements. '''
        self.record_delays = True
        self.last_input_time = 0
        self.inputs = []
        self.start_recording(mouse_move=record_movements)

    # This function will be called when an input is detected and adds a delay action to the inputs list if recording delays
    def record_delay(self):
        if self.record_delays:
            current_time = time()  # Get current time
            dt = current_time - self.last_input_time
            if dt > 0:
                self.inputs.append(f'delay_{dt}')
            self.last_input_time = current_time  # Store for next delay

    def start_recording(self, kb_press=True, kb_release=True, mouse_move=True, mouse_click=True, mouse_scroll=True):
        # The 5 parameters are bools that determine if the event should be recorded
        
        self.reset_keyboard_listener()
        self.reset_mouse_listener()

        self.keyboard_listener.on_press = self.on_press_record if kb_press else self.on_press_ignore # on_press_ignore has special functionality
        self.keyboard_listener.on_release = self.on_release_record if kb_release else self.on_event_ignore
        self.mouse_listener.on_move = self.on_move_record if mouse_move else self.on_event_ignore
        self.mouse_listener.on_click = self.on_click_record if mouse_click else self.on_event_ignore
        self.mouse_listener.on_scroll = self.on_scroll_record if mouse_scroll else self.on_event_ignore

        # Give user delay to get ready
        self.do_prep_delay(self.prep_time)

        self.recording = True

        if self.keep_initial_position and not self.appending:
            # Move to initial position
            x, y = self.mouse.position
            self.inputs.append(f'reset_mouse_position_{x}_{y}')
            
        self.last_input_time = time()

        if self.state_listener_active:
            self.state_change_listener.stop() # Avoid having multiple listeners running at once as it can cause issues apparently
            self.state_listener_active = False

        self.keyboard_listener.start()
        self.mouse_listener.start()
    
    def end_recording(self):
        self.recording = False 

        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.start_state_listener() # TODO: Might move this to an enable macro function and not here
                                    # This would be in the case where the macro is executed by a button press when enabled
        
        # If delays were recorded, remove the initial delay if that config is set
        if self.record_delays and not self.keep_initial_delay and not self.appending:
            # Find and remove first delay action
            for i, inp in enumerate(self.inputs):
                if inp.startswith('delay'):
                    self.inputs.pop(i)
                    break

        self.appending = False

    def do_prep_delay(self, delay):
        self.preparing = True
        # If delay is negative, wait for the user to press the end prep key before starting the delay
        if delay < 0:
            # Wait for the user to press the end prep key
            while self.preparing:
                sleep(0.01)
            delay = delay*-1
        sleep(delay)
        self.preparing = False

    # Functions to reset the listeners since you can't start the same listener twice
    def reset_keyboard_listener(self):
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press_ignore,
            on_release=self.on_event_ignore
        )

    def reset_mouse_listener(self):
        self.mouse_listener = mouse.Listener(
            on_move=self.on_event_ignore,
            on_click=self.on_event_ignore,
            on_scroll=self.on_event_ignore
        )

    def clear_macro(self):
        self.inputs = []
        self.replays = []

    ''' Event listeners '''

    # Each event listener will create a string representation of that specific event and add it to the inputs list

    # Key presses
    def on_press_record(self, key, injected=False):
        if self.check_state_change(key):
            return

        self.record_delay()

        key_name = self._key_to_string(key)

        # Ignore system events, which, as far as I know, start with < in their string form
        # Make sure we still keep the < key though.
        # Also ignore any unrecognized keys, which are Nonetype
        if key_name is None or (key_name.startswith('<') and key_name != '<'):
            return

        # Add metadata to see what the event was
        self.inputs.append(f'key_press_{key_name}')

    # Key releases
    def on_release_record(self, key, injected=False):

        key_name = self._key_to_string(key)

        if key_name is None or (key_name.startswith('<') and key_name != '<'):
            return
        
        # Sometimes end recording key is released just before ending the recording, so ignore it
        if key == self.end_recording_key and len(self.inputs) > 0:
            # If inputs isn't empty, then we were recording
            return
        
        # Note: a similar issue can occur with the end prep key when using a negative prep time
        # In this case, just set the prep time to be longer. I consider this case to be a user issue

        self.record_delay()

        key_name = self._key_to_string(key)
        self.inputs.append(f'key_release_{key_name}')

    # Mouse movements
    def on_move_record(self, x, y, injected=False):
        self.record_delay()

        # This seems wrong but it works great
        last_x, last_y = self.mouse.position

        # x and y are absolute coordinates
        self.inputs.append(f'mouse_move_{last_x}_{last_y}_to_{x}_{y}')

    # Mouse clicks and releases
    def on_click_record(self, x, y, button, pressed, injected=False):
        self.record_delay()

        # Handle the case where the click uses absolute coordinates
        if self.click_uses_coords:
            # Also adds a delay after moving, otherwise clicks were ingored in some games
            self.inputs.append(f'move_{x}_{y}_delay_{self.move_delay}')

        if pressed:
            self.inputs.append(f'mouse_press_{button}')

        else:
            self.inputs.append(f'mouse_release_{button}')

    # Mouse scrolls
    def on_scroll_record(self, x, y, dx, dy, injected=False):
        self.record_delay()

        self.inputs.append(f'mouse_scroll_{dx}_{dy}')

    def on_event_ignore(self, *args):
        # Generic function to ignore any event
        pass

    def on_press_ignore(self, key):
        # Ignores all key presses except for special ones that affect state
        # Such as the end recording key
        self.check_state_change(key)

    
    ''' State management '''

    def check_state_change(self, key):
        # Checks if the key pressed affects the state of the macro
        if key == self.end_prep_key and self.preparing:
            self.preparing = False
            return True
        if key == self.end_recording_key and self.recording:
            self.end_recording()
            return True
        if key == self.terminate_macro_key and self.executing:
            self.stop_macro()
            return True
        return False
    
    def start_state_listener(self):
        self.state_change_listener = keyboard.Listener(
            on_press=self.on_press_ignore,
            on_release=self.on_event_ignore
        )
        self.state_change_listener.start()
        self.state_listener_active = True


    ''' Macro execution '''

    def start_macro(self, n=1): # n is the number of times the macro will be executed
                                # If n is negative, the macro will be executed until stop_macro is called
        self.n = n
        self.executing = True
        if self.is_admin and self.block_input_when_executing:
            self.block_input()  # Block input when macro starts
        self.macro_thread = Thread(target=self._run_macro, daemon=True)
        self.macro_thread.start()   

    def _run_macro(self):
        while(self.executing):
            # Execute the macro
            for i in range(len(self.replays)):

                if not self.executing:  # Check if we should stop
                    return
                
                if self.pause: # Pause the macro
                    self.is_paused = True
                    while self.pause: 
                        sleep(0.01)
                    self.is_paused = False

                # If the input is a key press of the terminate macro key, ignore it
                terminate_key = self._key_to_string(self.terminate_macro_key)
                if self.replays[i].type == f'key_press_{terminate_key}':
                    self.terminate_macro_key = None

                self.replays[i]()

                self.terminate_macro_key = terminate_key

            self.n -= 1
            # If repeats remain, delay and repeat
            if self.n != 0:
                self.is_paused = True
                sleep(self.macro_repeat_delay)
                self.is_paused = False
            else:
                self.executing = False
                if self.is_admin and self.block_input_when_executing:
                    self.unblock_input()  # Restore input when macro stops
                return

    def stop_macro(self):
        self.executing = False
        if self.is_admin and self.block_input_when_executing:
            self.unblock_input() # Restore input when macro stops
        self.macro_thread.join() # Might hang if waiting for a delay execution to finish, not a problem

    def pause_macro(self):
        self.pause = True

    def resume_macro(self):
        self.pause = False


    ''' Input blocking '''
    def block_input(self, block=True):
        # Block/unblock all input except from macro
        # False = unblock, True = block
        result = user32.BlockInput(wintypes.BOOL(block))
        if not result:
            error = ctypes.get_last_error()
            raise Exception(f'Failed to {"block" if block else "unblock"} input: {error}')

    def unblock_input(self):
        self.block_input(False)


    ''' Macro management '''

    def save_macro(self, filename='macro.txt'):
        # Create saved_macros directory if it doesn't exist
        save_dir = os.path.join(os.path.dirname(__file__), 'saved_macros')
        os.makedirs(save_dir, exist_ok=True)
        
        # Save the macro to a file within the saved_macros directory
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'w') as f:
            for input in self.inputs:
                f.write(f'{input}\n')

        # Also load the functionality of the macro for upon saving
        self.load_macro()

    def load_from_file(self, file):
        # Load from saved_macros directory
        filepath = os.path.join(os.path.dirname(__file__), 'saved_macros', file)
        with open(filepath, 'r') as f:
            self.inputs = f.read().splitlines()

        self.load_macro()

    def load_macro(self):
        # Clear the current macro
        self.replays = []

        # Load the macro from the inputs list
        for inp in self.inputs:
            self._load_input(inp.strip())

    def _load_input(self, inp):
        # From each string in inputs, create a replay function for it and add it to the list

        if inp.startswith('key_press'):
            key = inp[10:] # Can't use split because the key name might contain underscores
            key = self._string_to_key(key)
            def replay_action():
                self.keyboard.press(key)


        elif inp.startswith('key_release'):
            key = inp[12:] # Can't use split because the key name might contain underscores
            key = self._string_to_key(key)
            def replay_action():
                self.keyboard.release(key)
        

        elif inp.startswith('mouse_move'):
            from_x, from_y = inp.split('_')[2:4]
            to_x, to_y = inp.split('_')[5:7]
            
            if self.use_absolute_coords:
                def replay_action():
                    self._move_mouse_absolute(int(to_x), int(to_y))

            else:
                dx = int(to_x) - int(from_x)
                dy = int(to_y) - int(from_y)
                def replay_action():
                    self._move_mouse_relative(dx, dy)

        
        elif inp.startswith('move'): # move_x_y_delay_z
            x, y = inp.split('_')[1:3]
            delay = float(inp.split('_')[4])
            def replay_action():
                self._move_mouse_absolute(int(x), int(y))
                sleep(delay)
            

        elif inp.startswith('mouse_press') or \
            inp.startswith('mouse_release'):
            
            button_str = inp.split('_')[2]
            # Example: button_str == "Button.left", so we extract "left"
            if button_str.startswith("Button."):
                button_name = button_str.split('.')[1]
                button = getattr(Button, button_name)
            else:
                button = button_str

            if inp.startswith('mouse_press'):
                def replay_action():
                    self.mouse.press(button)
            else:
                def replay_action():
                    self.mouse.release(button)


        elif inp.startswith('mouse_scroll'):
            dx, dy = inp.split('_')[2:]
            def replay_action():
                self.mouse.scroll(int(dx), int(dy))
            
            
        elif inp.startswith('delay'):
            delay = inp.split('_')[1]
            def replay_action():
                sleep(float(delay))


        elif inp.startswith('reset_mouse_position'):
            x, y = inp.split('_')[3:]
            def replay_action():
                self._move_mouse_absolute(int(x), int(y))

        else:
            print(f'Unknown input: {inp}')

        # Add metadata to see what the input was
        replay_action.type = inp
        self.replays.append(replay_action)


    ''' Macro Editing '''

    def append_sequence(self, record_movements=False):

        # We need to save this to not affect initial delay or record initial position regardless of config
        self.appending = True

        # Save the current macro
        inputs_before = self.inputs

        self.record_sequence(record_movements)

        # Add the new inputs to the end of the old inputs
        self.inputs = inputs_before + self.inputs

    def set_delays(self, delay):
        # Replace all delay functions with a set delay
        new_inp = f'delay_{delay}'
        for i, inp in enumerate(self.inputs):
            if inp.startswith('delay'):
                self.inputs[i] = new_inp

    def compress_movements(self, divisor=5):
        # Compress movements and delays to reduce how many there are
        # divisor is the number of movements to compress into one
        count = 0
        start = 0
        end = 0

        i = 0

        while i < len(self.inputs):
            inp = self.inputs[i]

            if inp.startswith('mouse_move'):
                
                if count == 0:
                    start = i

                if count == divisor: # Mark as end point, and don't include this movement in the compression, as end is excluded
                    end = i
                    # _compress_movement returns an index that accounts for the list size shrinking
                    i = self._compress_movement(start, end)
                    count = 0 # Reset count
                    continue

                count += 1

            elif not inp.startswith('delay'):
                # If we encounter a non-movement, non-delay input, reset the count

                # First, compress any group of movements that was ready to be compressed
                if count > 1:
                    i = self._compress_movement(start, i)
                
                count = 0

            i += 1

        # If there are any movements left after iterating through the list, compress them
        if count > 1:
            self._compress_movement(start, i)

        
    def _compress_movement(self, start, end):
        print(f'Compressing movements from {start} to {end}')
        # [start, end) is the range of movements to compress
        # Compress a series of movements and delays into a single movement and delay
        
        # Add up all the relative movements
        total_dx = 0
        total_dy = 0
        for i in range(start, end):
            if self.inputs[i].startswith('mouse_move'):
                start_x, start_y = self.inputs[i].split('_')[2:4]
                end_x, end_y = self.inputs[i].split('_')[5:7]

                dx = int(end_x) - int(start_x)
                dy = int(end_y) - int(start_y)

                total_dx += dx
                total_dy += dy

        # Find the first movement's start coordinates
        for i in range(start, end):
            if self.inputs[i].startswith('mouse_move'):
                initial_x, initial_y = self.inputs[i].split('_')[2:4]
                break

        # Add the total movement to the start coordinates
        end_x = int(initial_x) + total_dx
        end_y = int(initial_y) + total_dy

        # Note: we calculated the movment in a relative manner to work with moving game cameras
        
        # Add up all the delays
        new_delay = 0
        for i in range(start, end):
            if self.inputs[i].startswith('delay'):
                new_delay += float(self.inputs[i].split('_')[1])

        # Remove the old inputs
        for i in range(start, end):
            self.inputs.pop(start)

        # This index is for retuning the next compression start point, and accounts for the list size shrinking
        new_index = start + 1

        # Insert the new movement and delay
        self.inputs.insert(start, f'mouse_move_{initial_x}_{initial_y}_to_{end_x}_{end_y}')

        # If there is a delay, insert it and account for the extra element for new_index
        if new_delay > 0:
            self.inputs.insert(start, f'delay_{new_delay}')
            new_index += 1

        return new_index

    def remove_input(self, index):
        self.inputs.pop(index)
    

    ''' Properties '''
    @property
    def end_recording_key(self):
        return self._end_recording_key
    
    @end_recording_key.setter
    def end_recording_key(self, key):
        self._end_recording_key = self._set_key(key)
        
    @property
    def end_prep_key(self):
        return self._end_prep_key
    
    @end_prep_key.setter
    def end_prep_key(self, key):
        self._end_prep_key = self._set_key(key)

    @property
    def terminate_macro_key(self):
        return self._terminate_macro_key
    
    @terminate_macro_key.setter
    def terminate_macro_key(self, key):
        self._terminate_macro_key = self._set_key(key)
        
    
    def _set_key(self, key):
        if isinstance(key, str):
            return self._string_to_key(key)
        elif isinstance(key, Key) or isinstance(key, KeyCode):
            return key
        elif key is None:
            return None
        else:
            raise ValueError(f'Invalid key: {key}')

    
    ''' General helpers '''
    ''' Other helpers come directly after the function that needs them '''
    def _string_to_key(self, key_str):
        # Takes a string and converts it to the corrosponding key object, or None
        # Does not handle keycodes like 0x16
        # Only takes either a single character or a special key name, such as "shift" or "ctrl_l"
        if key_str is None:
            return None

        if len(key_str) == 1:
            # Regular character key
            return KeyCode.from_char(key_str)
        else:
            # Special key (like shift, ctrl, etc)
            return getattr(Key, key_str)

    def _key_to_string(self, key):
        # Takes a key object and converts it to a string
        if key is None:
            return None
        
        key_name = str(key)

        if isinstance(key, KeyCode):

            key_name = key.char

            # If the character is a control character, convert it to its corrosponding letter.
            # For letters, CTRL+<letter> often gives an ordinal less than 32.
            if key_name is not None and ord(key_name) < 32:
                # For example, ord('\x16') is 22, and 22 + 96 = 118, which is 'v'.
                key_name = chr(ord(key_name) + 96)

        else:
            # Special key (like shift, ctrl, etc)
            # Remove "Key." prefix
            key_name = key_name.split('.')[1]

        return key_name


    def _move_mouse_relative(self, dx, dy):
        # Move the mouse relative to the current position
        # pyautogui is much better at this than pynput
        #pyautogui.moveRel(dx, dy, duration=0)
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)
        print(f'Moved mouse by {dx}, {dy}')


    def _move_mouse_absolute(self, x, y):
        # Move mouse to pixel coordinates
        self.mouse.position = (x, y)