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
awareness = ctypes.c_int()
ctypes.windll.shcore.SetProcessDpiAwareness(2)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

user32 = ctypes.WinDLL('user32', use_last_error=True)

# TODO:
# - make sure all the keys can be recorded.
# - Idea: make a function that compresses consecutive mouse movements into less or one movement for efficiency
#    - This would especially help when speeding up a macro
#    - Be careful if compressing the delays as well, as set_delays with and without compressing them will not be the same

class Macro:
    def __init__(self):

        ''' Core Macro Variables '''
        self.inputs = [] # Inputs that the macro will execute
        self.last_input_time = 0 # Time of the last input

        ''' State Variables '''
        self.recording = False
        self.executing = False
        self.preparing = False
        self.pause = False
        self.is_paused = False
        self.is_admin = is_admin() # Admin needed to block input
        self.recording_move = False # Used as a lock to not record multiple mouse movements at once

        ''' Configuration Variables '''
        self.macro_repeat_delay = 1 # delay between each repeat of the macro
        self.record_delays = False
        self._end_recording_key = Key.esc # Key to end a recording, default is esc
        self._end_prep_key = Key.esc # Key to end the prep time, default is esc
        self._terminate_macro_key = Key.esc # Key to terminate the macro, default is esc
        self.prep_time = 0 # Time to wait before recording starts
        self.click_uses_absolute_coords = False # mouse will click at the coordinates recorded instead of just a click
        self.move_delay = 0.01 # delay between moving the mouse and clicking, only used if click_uses_absolute_coords is True
        self.block_input_when_executing = False # Only possible if admin, USE WITH CAUTION, as even terminate macro key will be blocked
        self.keep_initial_position = False # macro will reset the mouse to where it was at the start of recording

        ''' Controllers '''
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

        ''' Listeners '''
        # When recording is started, the callbacks for recording will be configured
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press_ignore,
            on_release=self.on_event_ignore
        )
        self.mouse_listener = mouse.Listener(
            on_move=self.on_event_ignore,
            on_click=self.on_event_ignore,
            on_scroll=self.on_event_ignore
        )
        # This listener will be active when not recording so that important keys can still be detected
        self.state_change_listener = keyboard.Listener(
            on_press=self.on_press_ignore,
            on_release=self.on_event_ignore
        )
        self.start_state_listener()
        


    ''' Input recording '''

    def record_basic_input(self):
        ''' Record basic input such as key presses and mouse clicks, ignoring mouse movements. '''
        # We don't want the end recording key to work here
        self.end_recording_key = None

        self.record_delays = False
        self.inputs = []
        threshold = 0
        if self.keep_initial_position:
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
        
    def record_basic_sequence(self):
        ''' Records a sequence of basic inputs, ignoring mouse movements. '''
        self.record_delays = True
        self.last_input_time = 0
        self.inputs = []
        self.start_recording(mouse_move=False)

    def record_full_sequence(self):
        ''' Records basic sequence as well as all mouse movements. '''
        self.record_delays = True
        self.last_input_time = 0
        self.inputs = []
        self.start_recording()

    # This function will be called when an input is detected and adds a delay action to the inputs list if recording delays
    def record_delay(self):
        if self.record_delays:
            current_time = time()  # Get current time
            dt = current_time - self.last_input_time
            if dt > 0:
                def delay_action():
                    sleep(dt)
                delay_action.type = f'delay_{dt}'
                self.inputs.append(delay_action)
            self.last_input_time = current_time  # Store for next delay

    def start_recording(self, kb_press=True, kb_release=True, mouse_move=True, mouse_click=True, mouse_scroll=True):
        # The 5 parameters are bools that determine if the event should be recorded
        self.keyboard_listener.on_press = self.on_press_record if kb_press else self.on_press_ignore # on_press_ignore has special functionality
        self.keyboard_listener.on_release = self.on_release_record if kb_release else self.on_event_ignore
        self.mouse_listener.on_move = self.on_move_record if mouse_move else self.on_event_ignore
        self.mouse_listener.on_click = self.on_click_record if mouse_click else self.on_event_ignore
        self.mouse_listener.on_scroll = self.on_scroll_record if mouse_scroll else self.on_event_ignore

        # Give user delay to get ready
        self.do_prep_delay(self.prep_time)

        self.recording = True

        if self.keep_initial_position:
            # Store initial position
            self.initial_position = self.mouse.position
            
            def reset_mouse_position():
                self.mouse.position = self.initial_position
            
            reset_mouse_position.type = f'reset_mouse_position_{self.initial_position[0]}_{self.initial_position[1]}'
            self.inputs.append(reset_mouse_position)

        self.state_change_listener.stop() # Avoid having multiple listeners running at once as it can cause issues apparently
        self.keyboard_listener.start()
        self.last_x, self.last_y = self.mouse.position # Record last x and y mouse position as initial position
        self.mouse_listener.start()
        
    def end_recording(self):
        self.recording = False 

        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.start_state_listener()

        # If delays were recorded, remove the initial delay
        if self.record_delays:
            # Find and remove first delay action
            for i, action in enumerate(self.inputs):
                if action.type.startswith('delay'):
                    self.inputs.pop(i)
                    break

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
            for i in range(len(self.inputs)):

                if not self.executing:  # Check if we should stop
                    return
                
                if self.pause: # Pause the macro
                    self.is_paused = True
                    while self.pause: 
                        sleep(0.01)
                    self.is_paused = False

                # If the input is a key press of the terminate macro key, ignore it
                terminate_key = self._key_to_string(self.terminate_macro_key)
                if self.inputs[i].type == f'key_press_{terminate_key}':
                    self.terminate_macro_key = None

                self.inputs[i]()

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


    ''' Event listeners '''

    # Each event listener will create a replay function for that specific event and add it to the inputs list

    # Key presses
    def on_press_record(self, key, injected=False):
        if self.check_state_change(key):
            return

        self.record_delay()

        key_name = self._key_to_string(key)

        if isinstance(key, KeyCode):

            # Ignore system events, which so far have started with < in their string form
            if key_name.startswith('<'):
                return

            def replay_action():
                self.keyboard.press(key_name)
        
        else:
            # Special key (like shift, ctrl, etc)
            def replay_action():
                self.keyboard.press(key)

        # Add metadata to see what the event was
        replay_action.type = 'key_press_' + key_name

        self.inputs.append(replay_action)

    # Key releases
    def on_release_record(self, key, injected=False):
        
        # Sometimes end recording key is released just before ending the recording, so ignore it
        if key == self.end_recording_key and len(self.inputs) > 0:
            # If inputs isn't empty, then we were recording
            return
        
        # Note: a similar issue can occur with the end prep key when using a negative prep time
        # In this case, just set the prep time to be longer. I consider this case to be a user issue

        self.record_delay()

        key_name = self._key_to_string(key)

        if isinstance(key, KeyCode):
            def replay_action():
                self.keyboard.release(key_name)
        
        else:
            # Special key (like shift, ctrl, etc)
            def replay_action():
                self.keyboard.release(key)
        

        # Add metadata to see what the event was
        replay_action.type = 'key_release_' + key_name

        self.inputs.append(replay_action)

    # Mouse movements
    def on_move_record(self, x_pos, y_pos, injected=False):

        # x and y parameters are not used, as it caused issues
        #  by returning different values than mouse.position, so we only use mouse.position

        # move movements need a special check. If the mouse is moved while this function is running,
        # then it can mess up movments, especially for slower computers, where it can't run this function
        # as often as the mouse is moved.
        if self.recording_move:
            return
        
        # Lock the recording of mouse movements
        self.recording_move = True

        self.record_delay()

        x, y = self.mouse.position

        # Calculate relative movement
        dx = x - self.last_x
        dy = y - self.last_y

        self.last_x = x
        self.last_y = y

        print('--------------------------------')
        print('x:', x, 'y:', y)
        print('last x:', self.last_x, 'last y:', self.last_y) # debug
        print('dx:', dx, 'dy:', dy) # debug

        def replay_action():
            # Move the mouse relative to the current position
            # We use the Windows api to simulate more "raw" mouse movement, allowing it to move the player camera in games
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, dx, dy, 0, 0)

        # Add metadata to see what the event was
        replay_action.type = f'mouse_move_{dx}_{dy}'

        self.inputs.append(replay_action)

        sleep(0.01)

        # Unlock the recording of mouse movements
        self.recording_move = False

    # Mouse clicks and releases
    def on_click_record(self, x, y, button, pressed, injected=False):
        self.record_delay()

        # Handle the case where the click uses absolute coordinates
        if self.click_uses_absolute_coords:
            # Wait for the mouse to move, otherwise clicks were ingored in some games
            def move_delay_action():
                self.mouse.position = (x, y)
                sleep(self.move_delay) 
            move_delay_action.type = f'move_{x}_{y}_delay_{self.move_delay}'
            self.inputs.append(move_delay_action)

        if pressed:
            def replay_action():
                self.mouse.press(button)

        else:
            def replay_action():
                self.mouse.release(button)

        # Add metadata to see what the event was
        replay_action.type = 'mouse_{click}_{button}'.format(click='press' if pressed else 'release', button=button)

        self.inputs.append(replay_action)

    # Mouse scrolls
    def on_scroll_record(self, x, y, dx, dy, injected=False):
        self.record_delay()
        def replay_action():
            self.mouse.scroll(dx, dy)

        # Add metadata to see what the event was
        replay_action.type = f'mouse_scroll_{dx}_{dy}'

        self.inputs.append(replay_action)

    def on_event_ignore(self, *args):
        # Generic function to ignore any event
        pass

    def on_press_ignore(self, key):
        # Ignores all key presses except for special ones that affect state
        # Such as the end recording key or the terminate macro key
        self.check_state_change(key)


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

    def remove_input(self, index):
        self.inputs.pop(index)

    def get_input_types(self):
        # Returns a list of the input types, which are easier to read than the input replay functions
        return [f"{i}: {input.type}" for i, input in enumerate(self.inputs)]
    
    def save_macro(self, filename='macro.txt'):
        # Create saved_macros directory if it doesn't exist
        save_dir = os.path.join(os.path.dirname(__file__), 'saved_macros')
        os.makedirs(save_dir, exist_ok=True)
        
        # Save the macro to a file within the saved_macros directory
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'w') as f:
            for input in self.inputs:
                f.write(f'{input.type}\n')

    def load_macro(self, from_file='macro.txt', to_list=None):
        if to_list is None:
            to_list = self.inputs
            
        # Load from saved_macros directory
        filepath = os.path.join(os.path.dirname(__file__), 'saved_macros', from_file)
        with open(filepath, 'r') as f:
            for line in f:
                # Each line describes an input, so create a replay function for it and add it to the inputs list
                self._add_input(line.strip(), to_list)

    def _add_input(self, inp, list):
        # Create a replay function for the input and add it to the list

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
            dx, dy = inp.split('_')[2:]
            def replay_action():
                # We use the Windows api to simulate more "raw" mouse movement, allowing it to move the player camera in games
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(dx), int(dy), 0, 0)

        
        elif inp.startswith('move'): # move_x_y_delay_z
            x, y = inp.split('_')[1:3]
            delay = float(inp.split('_')[4])
            def replay_action():
                self.mouse.position = (x, y)
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
                self.mouse.position = (x, y)

        else:
            print(f'Unknown input: {inp}')

        replay_action.type = inp
        list.append(replay_action)


    def set_delays(self, delay):
        # Replace all delay functions with a set delay
        def delay_action():
            sleep(delay)
        delay_action.type = f'delay_{delay}'
        for i, input in enumerate(self.inputs):
            if input.type.startswith('delay'):
                self.inputs[i] = delay_action
    

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
        if key_str == 'None':
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
            return 'None'
        
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

