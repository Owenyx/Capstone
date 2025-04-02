import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from EEG_Controller import Controller
from time import sleep
from Macro.Macro import Macro
import numpy as np
from threading import Thread
from copy import deepcopy


class FocusMacro:
    def __init__(self):

        ''' This class should be used alongside the Macro class to control it using brain activity '''

        ''' Controller '''
        self._macro = Macro()

        ''' Variables for tracking focus '''
        self.baseline_focus = 0 # This value is what all other relative focus values are compared to
        self.enable_threshold = 0 # At or above this percentage, the macro will be enabled, set to 0 for always enabled
                                  # This will be relative to the baseline focus, for example,
                                  # if the value is 1, the macro will be enabled when the user is at or above the baseline focus
                                  # if the value is 0.5, the macro will be enabled when the user is at or above 50% of the baseline focus
                                  # if the value is 1.5, the macro will be enabled when the user is at or above 150% of the baseline focus
        self.scaling_factor = 1 # At higher values, the macro frequency will increase and decrease more quickly, set to 0 for no scaling
        self.curr_focus = 0 # This is the current focus of the user
        self.rel_focus = 1 # This user's relative focus compared to the baseline focus, 1 means that the user is at the baseline focus
        self.constant_baseline = None # If this value is set to a number, it will be used as the baseline focus instead of the calculated one

        ''' Variables for controlling the macro '''
        self._base_repeat_delay = 1 # This is the delay between macro repeats when the user is at baseline focus
        self.macro.macro_repeat_delay = self.base_repeat_delay

        ''' Variables for collecting data '''
        self.update_delay = 1 # This is how often, in seconds, the focus values and macro parameters will be updated

        ''' Data for establishing basline focus '''
        # Data used to determine the baseline focus
        # Raw attention data is a good option for EEG data
        self.focus_data = None

        ''' Variables for parameter updating '''
        self.delay_indices = []
        self.original_delays = []
        self.updating = False

        ''' Callbacks '''
        self.macro.start_execution_callback = self.start_update_loop
        self.macro.stop_execution_callback = self.stop_update_loop

        ''' Other configuration variables '''
        self.constant_delay = False  # True means that the delays are NOT affected by the focus.
                                    # False means that the delays are affected by the focus.
        self.constant_frequency = False # True means that the macrofrequency is NOT affected by the focus.
                                        # False means that the frequency is affected by the focus.
        self.invert_scaling = False # True means that the scaling factor is inverted, 
                                    # meaning the macro will execute slower when the user is more focused


    ''' Properties '''

    @property
    def macro(self):
        return self._macro
    
    @macro.setter
    def macro(self, value):
        self._macro = value
        self._macro.start_execution_callback = self.start_update_loop
        self._macro.stop_execution_callback = self.stop_update_loop
        self._macro.macro_repeat_delay = self.base_repeat_delay
        

    @property
    def base_repeat_delay(self):
        return self._base_repeat_delay
    
    @base_repeat_delay.setter
    def base_repeat_delay(self, value):
        self._base_repeat_delay = value
        self.macro.macro_repeat_delay = value


    ''' Updating '''

    def _update_loop(self):

        # Wait until the focus data is available
        while self.focus_data is None or len(self.focus_data) == 0:
            sleep(0.1)

        # Should be called in a thread
        while self.updating:
            self.update_focus_data()
            self.update_macro_parameters()
            sleep(self.update_delay)

    def start_update_loop(self):
        # Since we will be modifying the delays, we need to save their original values

        # Save the indices of the delay inputs
        for i, input in enumerate(self.macro.inputs):
            if input.startswith('delay'):
                self.delay_indices.append(i)

        # Save the original delay values
        for i in self.delay_indices:
            self.original_delays.append(float(self.macro.inputs[i].split('_')[1]))

        self.updating = True
        self.update_thread = Thread(target=self._update_loop, daemon=True).start()

    def stop_update_loop(self):
        self.updating = False

        # Restore the original delays
        self.macro.load_macro()


    ''' Updating focus '''

    def update_focus_data(self):
        self.update_focus_baseline()
        self.update_user_focus()

    # We will use the focus data to determine the baseline focus
    def update_focus_baseline(self):
        if self.constant_baseline is not None:
            self.baseline_focus = self.constant_baseline
        else:
            self.baseline_focus = np.mean(self.focus_data) # Calculate the focus baseline as the mean of the focus data

    def update_user_focus(self):
        self.curr_focus = self.focus_data[-1] 
        self.rel_focus = self.curr_focus/self.baseline_focus 

        if self.rel_focus < self.enable_threshold:
            self.macro.pause_macro()
        else:
            self.macro.resume_macro()


    ''' Updating macro parameters '''

    def update_macro_parameters(self):
        self.update_macro_frequency()
        self.update_macro_delays()

    def update_macro_frequency(self):
        # Changes the macro_repeat_delay based on the relative focus of the user

        if self.constant_frequency:
            return
        
        factor = self.calculate_factor()
            
        new_delay = self.base_repeat_delay/factor

        print(f'new repeat delay: {new_delay}') # debug

        self.macro.macro_repeat_delay = new_delay

    def update_macro_delays(self):
        # This function uses the macro file that is currently loaded to create a list of inputs with new delays
        # It then replaces the old inputs with this new list
        # The macro file is not changed, and should never be changed outside of saving a different macro to it

        # Here's what we'll do
        ''' 
        When we initially load a macro file, we'll save the indices of the delay inputs and th
        Then when this function is called, we'll use the original values to calculate the new delays
        Then we'll replace the old inputs with the new ones
        '''

        if self.constant_delay:
            return
        
        new_replays = deepcopy(self.macro.replays)

        factor = self.calculate_factor()
            
        for i, old_delay in zip(self.delay_indices, self.original_delays):
            new_delay = old_delay/factor

            print(f'old delay: {old_delay}, new delay: {new_delay}') # debug

            def delay_action(delay=new_delay): # Assigning the default value prevents binding issues where all delay_actions use the same value
                sleep(delay)

            new_replays[i] = delay_action

        # Replace macro inputs when the macro is paused
        self.macro.pause_macro()
        while not self.macro.is_paused:
            sleep(0.001)
        self.macro.replays = new_replays

        # We only want to resume the macro if the user is at or above the enable threshold, otherwise the macro will resume when it shouldn't
        if self.rel_focus >= self.enable_threshold:
            self.macro.resume_macro()

    def calculate_factor(self):
        # Calculate factor based on distance from 1
        distance = abs(self.rel_focus - 1)

        import random
        self.rel_focus = random.choice([0.25, 0.5, 0.67, 0.75, 1, 1.25, 1.33, 1.5, 2]) # debug
        print(f'rel_focus: {self.rel_focus}') # debug
    
        if self.rel_focus >= 1:
            factor = 1 + distance * self.scaling_factor
        else:
            factor = 1/(1 + distance * self.scaling_factor)
        
        if self.invert_scaling:
            return 1/factor
        
        print(f'factor: {factor}') # debug

        return factor