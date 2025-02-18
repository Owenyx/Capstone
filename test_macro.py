from time import sleep, time
from threading import Thread
import numpy as np
from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import threading
import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL('user32', use_last_error=True)

class Macro:
    def __init__(self):

        ''' Macro '''
        self.__macro_repeat_delay = 1 # This will be the delay between each repeat of the macro
        self.__inputs = [] # Inputs that the macro will execute
        self.__last_input_time = 0 # Time of the last input
        self.__record_delays = False
        self.__recording = False
        self.__end_input_key = Key.esc # Key to end a recording, default is esc
        self.__executing = False
        self.__absolute_mouse_coords = False # If true, the mouse will move to the absolute coordinates 
                                                      # recorded instead of relative to the current position
        self.__block_input_when_executing = True # If true, user input will be blocked when the macro is executing
        self.keep_initial_position = False # If true, the macro will reset the mouse to where it was at the start of recording

        ''' Controllers '''
        self.__keyboard = KeyboardController()
        self.__mouse = MouseController()

        ''' Listeners '''
        # When recording is started, the callbacks for recording will be configured
        self.__keyboard_listener = keyboard.Listener(
            on_press=self.on_event_ignore,
            on_release=self.on_event_ignore
        )
        self.__mouse_listener = mouse.Listener(
            on_move=self.on_event_ignore,
            on_click=self.on_event_ignore,
            on_scroll=self.on_event_ignore
        )

    @property
    def recording(self):
        return self.__recording
    
    @property
    def inputs(self):
        return self.__inputs
    
    @property
    def executing(self):
        return self.__executing


    def remove_input(self, index):
        self.__inputs.pop(index)


    def start_macro(self, n=1): # n is the number of times the macro will be executed
                                # If n is negative, the macro will be executed until stop_macro is called
        self.__n = n
        self.__executing = True
        if self.__block_input_when_executing:
            self.block_input()  # Block input when macro starts
        self.__macro_thread = Thread(target=self.__run_macro, daemon=True)
        self.__macro_thread.start()   

    def __run_macro(self):
        while(self.__executing):
            # Execute the macro
            for i in range(len(self.__inputs)):
                if not self.__executing:  # Check if we should stop
                    return
                self.__inputs[i]()

            self.__n -= 1
            # If repeats remain, delay and repeat
            if self.__n != 0:
                sleep(self.__macro_repeat_delay)
            else:
                self.__executing = False
                self.unblock_input()  # Restore input when macro stops
                return


    def stop_macro(self):
        self.__executing = False
        self.unblock_input()  # Restore input when macro stops
        self.__macro_thread.join() # Might hang if waiting for a delay execution to finish


    ''' Input recording '''
    def record_basic_input(self):
        # Records basic input such as key presses and mouse clicks
        # Only ignores mouse movements
        self.__record_delays = False
        self.__inputs = []
        self.start_recording(mouse_move=False)
        while self.__recording:
            sleep(0.1)
            if len(self.__inputs) > 0:
                self.end_recording()
        self.__inputs = [self.__inputs[0]] # Only keep the first input
        # TODO: make it easy to optionally also record the release of the input
        
    def record_basic_sequence(self):
        # Records a sequence of basic inputs
        # Only ignores mouse movements
        self.__record_delays = True
        self.__last_input_time = 0
        self.__inputs = []
        self.start_recording(mouse_move=False)

    def record_full_sequence(self):
        # Records basic sequence as well as all mouse movements
        # TODO: Should add a delay before recording to let the user get ready
        self.__record_delays = True
        self.__last_input_time = 0
        self.__inputs = []
        self.start_recording()

    # This function will be called when an input is detected and adds a delay action to the inputs list if recording delays
    def input_detected(self):
        if self.__record_delays:
            current_time = time()  # Get current time
            dt = current_time - self.__last_input_time
            if dt > 0:
                def delay_action():
                    sleep(dt)
                delay_action.type = 'delay_{delay}_seconds'.format(delay=dt)
                self.__inputs.append(delay_action)
            self.__last_input_time = current_time  # Store for next delay

    def start_recording(self, kb_press=True, kb_release=True, mouse_move=True, mouse_click=True, mouse_scroll=True):
        # The 5 parameters are bools that determine if the event should be recorded
        self.__keyboard_listener.on_press = self.on_press_record if kb_press else self.on_event_ignore
        self.__keyboard_listener.on_release = self.on_release_record if kb_release else self.on_event_ignore
        self.__mouse_listener.on_move = self.on_move_record if mouse_move else self.on_event_ignore
        self.__mouse_listener.on_click = self.on_click_record if mouse_click else self.on_event_ignore
        self.__mouse_listener.on_scroll = self.on_scroll_record if mouse_scroll else self.on_event_ignore
        self.__recording = True

        if self.keep_initial_position:
            # Store initial position
            self.__initial_position = self.__mouse.position
            
            def reset_mouse_position():
                self.__mouse.position = self.__initial_position
            
            reset_mouse_position.type = 'reset_mouse_position'
            self.__inputs.append(reset_mouse_position)

        self.__keyboard_listener.start()
        self.__mouse_listener.start()
    
    def end_recording(self):
        self.__recording = False  # Set this first
        # Just stop the listeners
        self.__keyboard_listener.stop()
        self.__mouse_listener.stop()
        
        # If delays were recorded, remove the initial delay
        if self.__record_delays:
            # Find and remove first delay action
            for i, action in enumerate(self.__inputs):
                if action.type.startswith('delay'):
                    self.__inputs.pop(i)
                    break


    ''' Event listeners '''
    # Each event listener will create a replay function for that specific event and add it to the inputs list
    def on_press_record(self, key):
        self.input_detected()
        # Checks if the end input key was pressed
        if key == self.__end_input_key:
            self.end_recording()
            return

        def replay_action():
            if isinstance(key, KeyCode):
                # Regular character key
                self.__keyboard.press(key.char)
            else:
                # Special key (like shift, ctrl, etc)
                self.__keyboard.press(key)

        # Add metadata to see what the event was
        replay_action.type = 'key_press_' + str(key)

        self.__inputs.append(replay_action)
        
    def on_release_record(self, key):
        self.input_detected()
        def replay_action():
            if isinstance(key, KeyCode):
                # Regular character key
                self.__keyboard.release(key.char)
            else:
                # Special key (like shift, ctrl, etc)
                self.__keyboard.release(key)

        # Add metadata to see what the event was
        replay_action.type = 'key_release_' + str(key)

        self.__inputs.append(replay_action)
            
    def on_move_record(self, x, y):
        self.input_detected()
        if self.__absolute_mouse_coords:
            def replay_action():
                self.__mouse.position = (x, y)
        else:
            # Move the mouse relative to the current position
            dx = x - self.__mouse.position[0]
            dy = y - self.__mouse.position[1]
            def replay_action():
                self.__mouse.move(dx, dy)

        # Add metadata to see what the event was
        replay_action.type = 'mouse_move'

        self.__inputs.append(replay_action)
        
    def on_click_record(self, x, y, button, pressed):
        self.input_detected()
        if pressed:
            def replay_action():
                if self.__absolute_mouse_coords:
                    self.__mouse.position = (x, y)

                self.__mouse.click(button)
        else:
            def replay_action():
                self.__mouse.release(button)

        # Add metadata to see what the event was
        replay_action.type = 'mouse_{click}_{button}'.format(click='press' if pressed else 'release', button=button)

        self.__inputs.append(replay_action)
        
    def on_scroll_record(self, x, y, dx, dy):
        self.input_detected()
        def replay_action():
            self.__mouse.scroll(dx, dy)

        # Add metadata to see what the event was
        replay_action.type = 'mouse_scroll_{direction}'.format(direction='down' if dy < 0 else 'up')

        self.__inputs.append(replay_action)

    def on_event_ignore(self, *args):
        # Generic function to ignore any event
        # Still checks if the end input key was pressed,
        if args[0] == self.__end_input_key: # args[0] would be the key pressed if it was called for a key press event
            self.stop_macro()

    ''' Macro management '''
    def save_macro(self):
        pass

    def load_macro(self):
        pass


    ''' Input blocking '''

    def block_input(self, block=True):
        """Block/unblock all input except from macro"""
        # 0 = unblock, 1 = block
        result = user32.BlockInput(wintypes.BOOL(block))
        if not result:
            error = ctypes.get_last_error()
            raise Exception(f'Failed to {"block" if block else "unblock"} input: {error}')

    def unblock_input(self):
        self.block_input(False)


if __name__ == '__main__':
    macro = Macro()
    macro.keep_initial_position = True
    macro.record_full_sequence()
    print('Recording started')
    while macro.recording:
        sleep(0.1)
    print('Recording stopped')
    
    # Print recorded inputs
    print("\nRecorded inputs:")
    for i, action in enumerate(macro.inputs): 
        try:
            print(f"{i}: {action.type}")
        except:
            print(f"{i}: {action}")

    
    macro.start_macro(n=1)
    print('Replaying macro')
    while macro.executing:
        sleep(0.1)
    print('Replaying stopped')