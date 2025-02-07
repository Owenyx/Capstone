from time import sleep
import numpy as np
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

class Macro:
    def __init__(self):

        ''' Variables for tracking the macro '''
        self.macro_frequency = 0 # This will be the frequency of the macro
        self.macro_state = 0 # This will be the state of the macro (0 = off, 1 = on)

        ''' Macro '''
        self.__inputs = [] # This will be the inputs that the macro will execute
        self.__delays = [] # This will be the delays between the inputs
        # delay[i] is the delay BEFORE input[i] is executed
        # Both of these lists must be the same length

    def enter_input(self, input, delay):
        self.__inputs.append(input)
        self.__delays.append(delay)

    def remove_input(self, index):
        self.__inputs.pop(index)
        self.__delays.pop(index)

    def run_macro(self):
        while(1):
            for i in range(len(self.__inputs)): # For each input, execute the delay and input
                input = self.__inputs[i]
                delay = self.__delays[i]
                self.execute_input(input, delay)

            sleep(self.__macro_frequency)


    ''' Input execution '''
    def execute_input(self, input, delay):
        # Executes an individual delay and input
        pass


    ''' Input recording '''
    def record_basic_input(self):
        # Records basic input such as key presses and mouse clicks
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

    def record_basic_sequence(self):
        # Records a sequence of basic inputs
        pass

    def record_full_sequence(self):
        # Records basic sequence as well as all mouse movements
        # Should add a delay before recording to let the user get ready
        pass

    def monitor_input(self):
        def on_press(key):
            self.__inputs.append(f'kp_{key}')
            
        def on_release(key):
            self.__inputs.append(f'kr_{key}')
                
        def on_move(x, y):
            self.__inputs.append(f'mm_{x},{y}')
            
        def on_click(x, y, button, pressed):
            action = 'p' if pressed else 'r'
            self.__inputs.append(f'm{action}_{button}_{x},{y}')
            
        def on_scroll(x, y, dx, dy):
            direction = 'd' if dy < 0 else 'u'
            self.__inputs.append(f'ms_{direction}_{x},{y}')

        # Set up the listeners
        with keyboard.Listener(on_press=on_press, on_release=on_release) as k_listener, \
            mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as m_listener:
            k_listener.join()
            m_listener.join()

    def save_macro(self):
        pass

    def load_macro(self):
        pass
