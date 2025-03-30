import ctypes, sys
from ctypes import wintypes
from Macro import Macro
from time import sleep
from pynput.keyboard import KeyCode
import win32api

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def escalate_privileges():
    if not is_admin():
        # Re-run the program with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

user32 = ctypes.WinDLL('user32', use_last_error=True)


''' Different functions for testing '''

macro = Macro()

def record_single_input():
    global macro
    print('Basic input recording started')
    macro.record_single_input()
    while macro.recording:
        sleep(0.1)
    print('Basic input recording stopped')

def record_basic_sequence():
    global macro
    print('Prepping started')
    macro.record_sequence()
    print('Basic sequence recording started')
    while macro.recording:
        sleep(0.1)
    print('Basic sequence recording stopped')


def record_full_sequence():
    global macro
    print('Prepping started')  
    macro.record_sequence(record_movements=True) 
    print('Full sequence recording started')
    while macro.recording:
        sleep(0.1)
    print('Full sequence recording stopped')

    

if __name__ == '__main__':
    mode = 0

    macro.end_recording_key = 'esc' 
    macro.end_prep_key = 'esc'
    macro.terminate_macro_key = 'esc'

    macro.use_absolute_coords = True
    macro.keep_initial_delay = False
    macro.keep_initial_position = True
    macro.prep_time = -1

    if mode == 0:
        record_single_input()

        macro.save_macro('macro.txt')


    elif mode == 1:
        sleep(3)

        macro.load_from_file('macro.txt')
        macro.start_macro(1)
        while macro.executing:
            sleep(0.1)