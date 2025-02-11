from time import sleep, time
import numpy as np
from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

class Macro:
    def __init__(self):

        ''' Variables for tracking the macro '''
        self.macro_frequency = 0 # This will be the frequency of the macro
        self.macro_state = 0 # This will be the state of the macro (0 = off, 1 = on)

        ''' Macro '''
        self.__inputs = [] # Inputs that the macro will execute
        self.__last_input_time = 0 # Time of the last input
        self.__record_delays = False
        self.__recording = False

    def enter_input(self, input, delay):
        self.__inputs.append(input)

    def remove_input(self, index):
        self.__inputs.pop(index)

    def run_macro(self):
        while(1):
            for i in range(len(self.__inputs)): # For each input, execute the delay and input
                input = self.__inputs[i]
                self.execute_input(input)

            sleep(self.__macro_frequency)


    ''' Input execution '''
    def execute_input(self, input):
        # Executes an individual delay and input
        # extract input type and parameters from input string
        # The notation used for inputs is at the top of the file
        input_type = input.split('_')[0]
        input_params = input.split('_')[1:]
        
        if input_type == 'kp':
            self.keyboard.press(input_params[0])
        elif input_type == 'kr':
            self.keyboard.release(input_params[0])
        elif input_type == 'mm':
            self.mouse.move(input_params[0], input_params[1])

    ''' Input recording '''
    def record_basic_input(self):
        # Records basic input such as key presses and mouse clicks
        self.__record_delays = False
        self.__inputs = []
        self.keyboard = KeyboardController(self.on_press_record, self.on_release_record)
        self.mouse = MouseController(self.on_move_ignore, self.on_click_record, self.on_scroll_record)
        self.keyboard_listener.start()
        self.mouse_listener.start()
        self.__recording = True
        while self.__recording:
            sleep(0.1)
            if len(self.__inputs) > 0:
                self.end_input()
        self.__inputs = self.__inputs[0] # Only keep the first input
        # TODO: make it easy to optionally also record the release of the input
        

    def record_basic_sequence(self):
        # Records a sequence of basic inputs
        self.__record_delays = True
        self.__last_input_time = 0
        self.__inputs = []
        self.keyboard = KeyboardController(self.on_press_record, self.on_release_record)
        self.mouse = MouseController(self.on_move_ignore, self.on_click_record, self.on_scroll_record)
        self.keyboard_listener.start()
        self.mouse_listener.start()
        self.__recording = True

    def record_full_sequence(self):
        # Records basic sequence as well as all mouse movements
        # Should add a delay before recording to let the user get ready
        self.__record_delays = True
        self.__last_input_time = 0
        self.__inputs = []
        self.keyboard = KeyboardController(self.on_press_record, self.on_release_record)
        self.mouse = MouseController(self.on_move_record, self.on_click_record, self.on_scroll_record)
        self.keyboard_listener.start()
        self.mouse_listener.start()
        self.__recording = True

    # This function will be called when an input is detected and adds a delay action to the inputs list if recording delays
    def input_detected(self):
        if self.__record_delays:
            def delay_action():
                sleep(time.time() - self.__last_input_time)
            self.__last_input_time = time.time()
            self.__inputs.append(delay_action)
    
    def end_input(self):
        # Stop both listeners
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.__recording = False

    ''' Event listeners '''
    # Each event listener will create a replay function for that specific event and add it to the inputs list
    def on_press_record(self, key):
        # Checks if the end input key was pressed
        if key == self.end_input_key:
            self.end_input()

        def replay_action():
            self.input_detected()
            if isinstance(key, KeyCode):
                # Regular character key
                self.keyboard.press(key.char)
            else:
                # Special key (like shift, ctrl, etc)
                self.keyboard.press(key)
        
    def on_release_record(self, key):
        def replay_action():
            self.input_detected()
            if isinstance(key, KeyCode):
                # Regular character key
                self.keyboard.release(key.char)
            else:
                # Special key (like shift, ctrl, etc)
                self.keyboard.release(key)
            
    def on_move_record(self, x, y):
        def replay_action():
            self.input_detected()
            self.mouse.move(x, y)
        
    def on_click_record(self, x, y, button, pressed):
        if pressed:
            def replay_action():
                self.input_detected()
                self.mouse.click(button, x, y)
        else:
            def replay_action():
                self.mouse.release(button)
        
    def on_scroll_record(self, x, y, dx, dy):
        def replay_action():
            self.input_detected()
            self.mouse.scroll(x, y, dx, dy)

    # These event listeners will be used to ignore events instead, so that recorded events can be configurable
    def on_press_ignore(self, key):
        # Still checks if the end input key was pressed
        if key == self.end_input_key:
            self.end_input()

    def on_release_ignore(self, key):
        pass

    def on_move_ignore(self, x, y):
        pass

    def on_click_ignore(self, x, y, button, pressed):
        pass

    def on_scroll_ignore(self, x, y, dx, dy):
        pass   

    ''' Macro management '''
    def save_macro(self):
        pass

    def load_macro(self):
        pass

