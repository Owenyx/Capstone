import ctypes, sys
from ctypes import wintypes
from Macro import Macro
from time import sleep
from pynput.keyboard import KeyCode

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

def print_input_types(macro):
    types = macro.get_input_types()

    for type in types:
        print(type)

def test_basic_input():
    macro = Macro()
    macro.keep_initial_position = True
    print('Basic input recording started')
    macro.record_basic_input()
    while macro.recording:
        sleep(0.1)
    print('Basic input recording stopped')

    print_input_types(macro)

def test_basic_sequence():
    macro = Macro()
    macro.end_recording_key = KeyCode.from_char('.')
    macro.prep_time = -0.000001
    macro.click_uses_coords = True
    print('Basic sequence recording started')
    macro.record_basic_sequence()
    while macro.recording:
        sleep(0.1)
    print('Basic sequence recording stopped')

    print_input_types(macro)

    sleep(3)

    macro.start_macro(1)
    print('Replaying macro')
    while macro.executing:
        sleep(0.1)
    print('Replaying stopped')

def test_full_sequence():
    macro = Macro()
    macro.end_recording_key = KeyCode.from_char('.')
    macro.prep_time = -0.000001
    macro.keep_initial_position = True
    print('Full sequence recording started')
    macro.record_full_sequence() 
    while macro.recording:
        sleep(0.1)
    print('Full sequence recording stopped')

    print_input_types(macro)

    sleep(3)


    macro.set_delays(0.0001)

    macro.start_macro(1)
    print('Replaying macro')
    while macro.executing:
        sleep(0.1)
    print('Replaying stopped')

def click_spam():
    macro = Macro()
    macro.prep_time = -0.000001
    macro.macro_repeat_delay = 0.0000000001
    print('Click spam recording started')
    macro.record_basic_sequence()
    while macro.recording:
        sleep(0.1)
    print('Click spam recording stopped')

    macro.set_delays(0.00000001)
    print_input_types(macro)
    sleep(3)

    macro.start_macro(10000)
    print('Replaying macro')
    while macro.executing:
        sleep(0.1)
    print('Replaying stopped')
    

if __name__ == '__main__':
    click_spam()
