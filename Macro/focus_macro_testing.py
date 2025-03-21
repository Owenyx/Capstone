from FocusMacro import FocusMacro
from time import sleep
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from EEG_Controller import Controller

controller = Controller()

controller.storage_time = 15

print('Searching for sensors...')
if not controller.find_and_connect():
    print('Failed to connect to sensors')
    exit()
print('Connected to sensors')
sleep(1)

controller.start_resist_collection()
print("Press Enter to stop collecting resistance data...")

import msvcrt
while True:
    sleep(1)
    print('O1:', controller.deques['resist']['O1']['values'][-1])
    print('O2:', controller.deques['resist']['O2']['values'][-1]) 
    print('T3:', controller.deques['resist']['T3']['values'][-1])
    print('T4:', controller.deques['resist']['T4']['values'][-1])
    
    if msvcrt.kbhit():
        if msvcrt.getch() == b'\r':
            break

controller.stop_collection()

controller.start_emotions_bipolar_collection()

while not controller.bipolar_is_calibrated:
    sleep(0.1)
    print(controller.bipolar_calibration_progress)


focus_macro = FocusMacro()

focus_macro.constant_baseline = 35

#focus_macro.scaling_factor = 10
#focus_macro.invert_scaling = True

focus_macro.base_repeat_delay = 1

focus_macro.update_focus_delay = 0.2
focus_macro.update_parameters_delay = 0.2

focus_macro.constant_delay = False

focus_macro.load_macro('macro.txt')

focus_macro.focus_data = controller.deques['emotions_bipolar']['attention']['raw']['values']

focus_macro.start_macro()

while focus_macro.macro.executing:
    sleep(0.2)
    print('curr_focus:', focus_macro.curr_focus)
    print('rel_focus:', focus_macro.rel_focus)
    print('factor:', focus_macro.calculate_factor())

controller.stop_collection()