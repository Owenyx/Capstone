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

        ''' While the Macro class deals with both recording and execution, this class only deals with execution '''

        ''' Controller '''
        self.macro = Macro()

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
        self.original_inputs = []
        self.original_delays = []

        ''' Other configuration variables '''
        self.constant_delay = False  # True means that the delays are NOT affected by the focus.
                                    # False means that the delays are affected by the focus.
        self.constant_frequency = False # True means that the macrofrequency is NOT affected by the focus.
                                        # False means that the frequency is affected by the focus.
        self.invert_scaling = False # True means that the scaling factor is inverted, 
                                    # meaning the macro will execute slower when the user is more focused


    ''' Properties '''
    @property
    def base_repeat_delay(self):
        return self._base_repeat_delay
    
    @base_repeat_delay.setter
    def base_repeat_delay(self, value):
        self._base_repeat_delay = value
        self.macro.macro_repeat_delay = value
    

    ''' Loading macros '''
    def load_macro(self, filename):
        self.macro.load_from_file(filename)

        # Save the original inputs. A reference is okay as we won't modify this list
        self.original_inputs = self.macro.replays

        # Save the indices of the delay inputs
        for i, input in enumerate(self.original_inputs):
            if input.type.startswith('delay'):
                self.delay_indices.append(i)

        # Save the original delay values
        for i in self.delay_indices:
            self.original_delays.append(float(self.original_inputs[i].type.split('_')[1]))


    ''' Updating '''

    def _update_loop(self):
        # Should be called in a thread
        while self.macro.executing:
            self.update_focus_data()
            self.update_macro_parameters()
            sleep(self.update_delay)

        
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
        
        new_inputs = deepcopy(self.original_inputs)

        factor = self.calculate_factor()
            
        for i, old_delay in zip(self.delay_indices, self.original_delays):
            new_delay = old_delay/factor

            def delay_action(delay=new_delay): # Assigning the default value prevents binding issues where all delay_actions use the same value
                sleep(delay)

            delay_action.type = f'delay_{new_delay}'
            new_inputs[i] = delay_action

        # Replace macro inputs when the macro is paused
        self.macro.pause_macro()
        while not self.macro.is_paused:
            sleep(0.01)
        self.macro.replays = new_inputs

        # We only want to resume the macro if the user is at or above the enable threshold, otherwise the macro will resume when it shouldn't
        if self.rel_focus >= self.enable_threshold:
            self.macro.resume_macro()

    def calculate_factor(self):
        # Calculate factor based on distance from 1
        distance = abs(self.rel_focus - 1)

        if self.rel_focus >= 1:
            factor = 1 + distance * self.scaling_factor
        else:
            factor = 1/(1 + distance * self.scaling_factor)
        
        if self.invert_scaling:
            return 1/factor
        
        return factor


    ''' Macro execution '''

    def start_macro(self):
        self.macro.start_macro(-1)
        self.update_thread = Thread(target=self._update_loop, daemon=True).start()

    def stop_macro(self):
        self.macro.stop_macro()
        self.update_thread.join()
