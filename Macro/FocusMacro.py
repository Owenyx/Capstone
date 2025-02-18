from Controller import Controller
from time import sleep
from Macro import Macro
import numpy as np


class BrainBit_Macro_Bridge:
    def __init__(self):

        ''' Controllers '''
        self.BB_Controller = Controller()
        self.macro = Macro()

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

