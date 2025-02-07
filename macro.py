from Controller import Controller
from time import sleep
import numpy as np
from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController


''' Notation used for tracking macro inputs '''

# Keyboard Events:
# kp_k = k key pressed
# kr_k = k key released

# Mouse Button Events:
# mp_b_x,y = mouse button b pressed at x,y
# mr_b_x,y = mouse button b released at x,y

# Mouse Movement Events:
# mm_x,y = mouse moved to x,y
# ms_d_x,y = mouse scrolled direction d (u = up, d = down) at x,y

# Special Events:
# d_t = delay t seconds  --  In this case we would remove the delay list, which we probably will
# sp_n = loop n times
# ep = marker for end of loop

class Macro:
    def __init__(self):
        # The following values are default, and can be changed by the user

        self.eeg = Controller()

        ''' Variables for tracking focus '''
        self.baseline_focus = 0 # This value is considered as our midpoint (50%) of focus, and will be based on recent data
        self.enable_threshold = 0.5 # Above this percentage, the macro will be enabled, set to 0 for always enabled
        self.scaling_factor = 1 # At higher values, the macro frequency will increase and decrease more quickly, set to 0 for no scaling
        self.curr_focus = 0 # This is the current focus of the user
        self.rel_focus = 1 # This user's relative focus compared to the baseline focus, 1 means that the user is at the baseline focus

        ''' Variables for collecting data '''
        self.cutoff_time = 60 # We will use the last cutoff_time seconds of data to calculate the baseline focus
        self.sampling_freq = 25 # depends on device used
        self.__total_values = self.cutoff_time*self.sampling_freq # This is how many values the mean must be based off of according to the cutoff and freq.
        self.update_interval = 1 # This is how often, in seconds, the baseline focus will be updated, might not be needed
        
        ''' Variables for tracking the macro '''
        self.macro_frequency = 0 # This will be the frequency of the macro
        self.macro_state = 0 # This will be the state of the macro (0 = off, 1 = on)

        ''' Data for establishing basline focus '''
        # We will use the raw attention to determine the baseline focus, but this may change at a later date
        self.__focus_data = self.eeg.deques['emotions_bipolar']['attention']['raw']['values']
        self.__timestamps = self.eeg.deques['emotions_bipolar']['attention']['raw']['timestamps'] # Might not be needed

        ''' Macro '''
        self.__inputs = [] # This will be the inputs that the macro will execute
        self.__delays = [] # This will be the delays between the inputs
        # delay[i] is the delay BEFORE input[i] is executed
        # Both of these lists must be the same length

        ''' Other configuration variables '''
        self.constant_delay = True # True means that the delays are NOT affected by the focus, False means that the delays are affected by the focus
        self.constant_frequency = False # True means that the macrofrequency is NOT affected by the focus, False means that the frequency is affected by the focus
        # By default, the macro frequency will depend on the focus but not the delays
        #self.invert_scaling = False # True means that the scaling factor is inverted, meaning the macro will execute slower when the user is more focused

    # We will use the focus data to determine the baseline focus
    def update_focus_baseline(self):
        self.baseline_focus = np.mean(self.__focus_data[-self.__total_values:]) # Calculate the mean of the last total_values values

    def update_user_focus(self):
        self.curr_focus = self.__focus_data[-1] # This is the current focus of the user
        self.rel_focus = self.curr_focus/self.baseline_focus # This is the relative focus of the user

    def enter_input(self, input, delay):
        self.__inputs.append(input)
        self.__delays.append(delay)

    def remove_input(self, index):
        self.inputs.pop(index)
        self.delays.pop(index)

    def run_macro(self):
        while(1):
            self.update_focus_baseline()
            self.update_user_focus()
            for i in range(len(self.inputs)): # For each input, execute the delay and input
                input = self.inputs[i]
                delay = self.delays[i]
                if not self.constant_delay:
                    delay = delay/self.rel_focus # Scale the delay by the relative focus
                self.execute_input(input, delay)

            freq = self.macro_frequency
            if not self.constant_frequency:
                freq = freq/self.rel_focus # Scale the frequency by the relative focus
            sleep(freq)

    def execute_input(self, input, delay):
        # Executes delay and then the input
        pass

    def record_basic_input(self):
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

    ''' Ai made this input monitoring code, still need to learn/refine '''
    def monitor_input():
        def on_press(key):
            try:
                print(f'Key pressed: {key.char}')
            except AttributeError:
                print(f'Special key pressed: {key}')
            
        def on_release(key):
            print(f'Key released: {key}')
            if key == Key.esc:
                return False
                
        def on_move(x, y):
            print(f'Mouse moved to ({x}, {y})')
            
        def on_click(x, y, button, pressed):
            action = 'Pressed' if pressed else 'Released'
            print(f'Mouse {action} at ({x}, {y}) with {button}')
            
        def on_scroll(x, y, dx, dy):
            direction = 'down' if dy < 0 else 'up'
            print(f'Scrolled {direction} at ({x}, {y})')

        # Set up the listeners
        with keyboard.Listener(on_press=on_press, on_release=on_release) as k_listener, \
            mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as m_listener:
            k_listener.join()
            m_listener.join()
    '''------------------------------------------------------------------------------------------------'''
