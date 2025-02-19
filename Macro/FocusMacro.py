from Controller import Controller
from time import sleep
from Macro import Macro
import numpy as np
from threading import Thread

class FocusMacro:
    def __init__(self):

        ''' Controllers '''
        self.eeg_Controller = Controller()
        self.macro = Macro()

        ''' Variables for tracking focus '''
        self.baseline_focus = 0 # This value is considered as our midpoint (50%) of focus, and will be based on recent data
        self.enable_threshold = 0.5 # Above this percentage, the macro will be enabled, set to 0 for always enabled
        self.scaling_factor = 1 # At higher values, the macro frequency will increase and decrease more quickly, set to 0 for no scaling
        self.curr_focus = 0 # This is the current focus of the user
        self.rel_focus = 1 # This user's relative focus compared to the baseline focus, 1 means that the user is at the baseline focus

        ''' Variables for controlling the macro '''
        self.base_repeat_delay = 1 # This is the delay between macro repeats when the user is at baseline focus
        self.macro.macro_repeat_delay = self.base_repeat_delay

        ''' Variables for collecting data '''
        self.cutoff_time = 60 # We will use the last cutoff_time seconds of data to calculate the baseline focus
        self.eeg_Controller.storage_time = self.cutoff_time # Controller will only store data for the last cutoff_time seconds
        self.update_delay = 1 # This is how often, in seconds, the baseline focus will be updated

        ''' Data for establishing basline focus '''
        # We will use the raw attention by default to determine the baseline focus, but this may change at a later date
        self.focus_data = self.eeg_Controller.deques['emotions_bipolar']['attention']['raw']['values']

        ''' Other configuration variables '''
        self.constant_delay = True  # True means that the delays are NOT affected by the focus.
                                    # False means that the delays are affected by the focus.
        self.constant_frequency = False # True means that the macrofrequency is NOT affected by the focus.
                                        # False means that the frequency is affected by the focus.
        # By default, the macro frequency will depend on the focus but the delays won't be affected
        self.invert_scaling = False # True means that the scaling factor is inverted, 
                                    # meaning the macro will execute slower when the user is more focused
    

    ''' Updating focus '''
    # We will use the focus data to determine the baseline focus
    def update_focus_baseline(self):
        self.baseline_focus = np.mean(self.focus_data) # Calculate the mean of up to the last cutoff_time values

    def update_user_focus(self):
        self.curr_focus = self.focus_data[-1] # This is the current focus of the user
        self.rel_focus = self.curr_focus/self.baseline_focus # This is the relative focus of the user


    ''' Updating macro parameters '''

    def update_macro_parameters(self):
        self.update_macro_frequency()
        self.update_macro_delays()
        sleep(self.update_delay)

    def update_macro_frequency(self):
        # Changes the macro_repeat_delay based on the relative focus of the user

        if self.constant_frequency:
            return
        
        new_delay = self.base_repeat_delay/(self.rel_focus*self.scaling_factor)

        if self.invert_scaling:
            new_delay = 1/new_delay

        self.macro.macro_repeat_delay = new_delay

    def update_macro_delays(self):
        # This will probably cause runtime error of trying to mutate a list while iterating over it
        # What we could od is make a new list with new delays using a thread and pause just to switch input lists

        if self.constant_delay:
            return
        
        for i, input in enumerate(self.macro.inputs):
            if input.type.startswith('delay'):

                old_delay = float(input.type.split('_')[1])
                # Reduce delay on higher focus
                new_delay = old_delay/(self.rel_focus*self.scaling_factor)

                if self.invert_scaling:
                    new_delay = 1/new_delay

                def delay_action():
                    sleep(new_delay)
                delay_action.type = f'delay_{new_delay}'
                self.macro.inputs[i] = delay_action

    ''' Macro execution '''

    def start_macro(self):
        self.macro.start_macro()
        self.update_thread = Thread(target=self._parameter_update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

    def stop_macro(self):
        self.macro.stop_macro()
        self.update_thread.join()
