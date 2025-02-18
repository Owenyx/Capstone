from time import sleep, time
from threading import Thread, Event
from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import ctypes, sys
from ctypes import wintypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

user32 = ctypes.WinDLL('user32', use_last_error=True)

# TODO:
# - Saving and loading macros

class Macro:
    def __init__(self):

        ''' Core Macro Variables '''
        self.inputs = [] # Inputs that the macro will execute
        self.last_input_time = 0 # Time of the last input

        ''' State Variables '''
        self.recording = False
        self.executing = False
        self.is_admin = is_admin() # Admin needed to block input

        ''' Configuration Variables '''
        self.macro_repeat_delay = 1 # delay between each repeat of the macro
        self.record_delays = False
        self.prep_time = 0 # Time to wait before recording starts
        self.end_recording_key = Key.esc # Key to end a recording, default is esc
        self.end_prep_key = Key.esc # Key to end the prep time, default is esc
        self.click_uses_coords = False # mouse will click at the coordinates recorded instead of just a click
        self.block_input_when_executing = True
        self.keep_initial_position = False # macro will reset the mouse to where it was at the start of recording

        ''' Controllers '''
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

        ''' Listeners '''
        # When recording is started, the callbacks for recording will be configured
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_event_ignore,
            on_release=self.on_event_ignore
        )
        self.mouse_listener = mouse.Listener(
            on_move=self.on_event_ignore,
            on_click=self.on_event_ignore,
            on_scroll=self.on_event_ignore
        )


    ''' Input recording '''

    def record_basic_input(self):
        # Records basic input such as key presses and mouse clicks
        # Only ignores mouse movements

        # We don't want the end recording key to work here
        self.end_recording_key = None

        self.record_delays = False
        self.inputs = []
        threshold = 0
        if self.keep_initial_position:
            threshold = 1 # Keep initial position adds an input to the start
        # Don't record key releases or mouse movements
        self.start_recording(kb_release=False, mouse_move=False)
        while self.recording:
            sleep(0.01)
            if len(self.inputs) > threshold:
                self.end_recording()
        self.inputs = self.inputs[:threshold+1] # Keep first threshold+1 items

        # Reset the end recording key
        self.end_recording_key = Key.esc
        
    def record_basic_sequence(self):
        # Records a sequence of basic inputs
        # Only ignores mouse movements
        self.record_delays = True
        self.last_input_time = 0
        self.inputs = []
        self.start_recording(mouse_move=False)

    def record_full_sequence(self):
        # Records basic sequence as well as all mouse movements
        self.record_delays = True
        self.last_input_time = 0
        self.inputs = []
        self.start_recording()

    # This function will be called when an input is detected and adds a delay action to the inputs list if recording delays
    def input_detected(self):
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
        self.keyboard_listener.on_press = self.on_press_record if kb_press else self.on_event_ignore
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

        self.keyboard_listener.start()
        self.mouse_listener.start()
    
    def end_recording(self):
        self.recording = False  # Set this first
        # Just stop the listeners
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        
        # If delays were recorded, remove the initial delay
        if self.record_delays:
            # Find and remove first delay action
            for i, action in enumerate(self.inputs):
                if action.type.startswith('delay'):
                    self.inputs.pop(i)
                    break

    def do_prep_delay(self, delay):
        # If delay is positive, wait for the delay to pass
        if delay >= 0:
            sleep(delay)
        # If delay is negative, wait for the user to press the end prep key AND wait for the delay to pass
        else:
            delay = delay*-1
            # Create an event to wait for the key press
            wait_event = Event()
            
            def on_press(key):
                if key == self.end_prep_key:
                    wait_event.set()  # Signal that key was pressed
                    return False  # Stop listener
                
            # Start temporary listener to wait for key
            with keyboard.Listener(on_press=on_press) as listener:
                wait_event.wait()  # Wait for key press
            
            sleep(delay)


    ''' Macro execution '''

    def start_macro(self, n=1): # n is the number of times the macro will be executed
                                # If n is negative, the macro will be executed until stop_macro is called
        self.n = n
        self.executing = True
        if self.is_admin and self.block_input_when_executing:
            self.block_input()  # Block input when macro starts
        self.macro_thread = Thread(target=self.__run_macro, daemon=True)
        self.macro_thread.start()   

    def __run_macro(self):
        while(self.executing):
            # Execute the macro
            for i in range(len(self.inputs)):
                if not self.executing:  # Check if we should stop
                    return
                self.inputs[i]()

            self.n -= 1
            # If repeats remain, delay and repeat
            if self.n != 0:
                sleep(self.macro_repeat_delay)
            else:
                self.executing = False
                if self.is_admin and self.block_input_when_executing:
                    self.unblock_input()  # Restore input when macro stops
                return

    def stop_macro(self):
        self.executing = False
        if self.is_admin and self.block_input_when_executing:
            self.unblock_input()  # Restore input when macro stops
        self.macro_thread.join() # Might hang if waiting for a delay execution to finish


    ''' Event listeners '''

    # Each event listener will create a replay function for that specific event and add it to the inputs list
    def on_press_record(self, key):
        self.input_detected()
        # Checks if the end input key was pressed
        if key == self.end_recording_key:
            self.end_recording()
            return

        def replay_action():
            if isinstance(key, KeyCode):
                # Regular character key
                self.keyboard.press(key.char)
            else:
                # Special key (like shift, ctrl, etc)
                self.keyboard.press(key)

        # Add metadata to see what the event was
        replay_action.type = 'key_press_' + str(key)

        self.inputs.append(replay_action)
        
    def on_release_record(self, key):
        self.input_detected()
        def replay_action():
            if isinstance(key, KeyCode):
                # Regular character key
                self.keyboard.release(key.char)
            else:
                # Special key (like shift, ctrl, etc)
                self.keyboard.release(key)

        # Add metadata to see what the event was
        replay_action.type = 'key_release_' + str(key)

        self.inputs.append(replay_action)
            
    def on_move_record(self, x, y):
        self.input_detected()
        # Needed for relative movement
        dx = x - self.mouse.position[0]
        dy = y - self.mouse.position[1]

        def replay_action():
            # Move the mouse relative to the current position
            self.mouse.move(dx, dy)

        # Add metadata to see what the event was
        replay_action.type = f'mouse_move_{dx}_{dy}'

        self.inputs.append(replay_action)
        
    def on_click_record(self, x, y, button, pressed):
        self.input_detected()
        if pressed:

            # Handle the case where the click uses absolute coordinates
            if self.click_uses_coords:
                move_delay = 0.01 # Wait for the mouse to move, otherwise clicks were ingored in some games
                def move_delay_action():
                    self.mouse.position = (x, y)
                    sleep(move_delay) 
                move_delay_action.type = f'mouse_move_{x}_{y}_delay_{move_delay}'
                self.inputs.append(move_delay_action)

            def replay_action():
                self.mouse.press(button)  # Use press() instead of click()

        else:
            def replay_action():
                self.mouse.release(button)

        # Add metadata to see what the event was
        replay_action.type = 'mouse_{click}_{button}'.format(click='press' if pressed else 'release', button=button)
        if self.click_uses_coords:
            replay_action.type += f'_{x}_{y}'

        self.inputs.append(replay_action)
        
    def on_scroll_record(self, x, y, dx, dy):
        self.input_detected()
        def replay_action():
            self.mouse.scroll(dx, dy)

        # Add metadata to see what the event was
        replay_action.type = f'mouse_scroll_{dx}_{dy}'

        self.inputs.append(replay_action)

    def on_event_ignore(self, *args):
        # Generic function to ignore any event
        # Still checks if the end input key was pressed,
        if args[0] == self.end_recording_key: # args[0] would be the key pressed if it was called for a key press event
            self.stop_macro()


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


    ''' Other functions '''

    def remove_input(self, index):
        self.inputs.pop(index)

    def get_input_types(self):
        # Returns a list of the input types, which are easier to read than the input replay functions
        return [f"{i}: {input.type}" for i, input in enumerate(self.inputs)]
    
    def save_macro(self, filename):
        with open(filename, 'w') as f:
            for input in self.inputs:
                f.write(f'{input.type}\n')

    def set_delays(self, delay):
        # Replace all delay functions with a set delay
        def delay_action():
            sleep(delay)
        delay_action.type = f'delay_{delay}'
        for i, input in enumerate(self.inputs):
            if input.type.startswith('delay'):
                self.inputs[i] = delay_action

