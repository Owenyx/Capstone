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
    macro.prep_time = 1
    print('Basic input recording started')
    macro.record_basic_input()
    while macro.recording:
        sleep(0.1)
    print('Basic input recording stopped')

def record_basic_sequence():
    global macro
    macro.prep_time = 1
    macro.click_uses_absolute_coords = True
    print('Basic sequence recording started')
    macro.record_sequence()
    while macro.recording:
        sleep(0.1)
    print('Basic sequence recording stopped')


def record_full_sequence():
    global macro
    macro.prep_time = -0.000001
    macro.keep_initial_position = True
    print('Full sequence recording started')  
    macro.record_sequence(record_movements=True) 
    while macro.recording:
        sleep(0.1)
    print('Full sequence recording stopped')


    '''
    sleep(1)
    macro.start_macro(1)
    while macro.executing:
        sleep(0.1)
    print('Replaying stopped')
    '''
    

if __name__ == '__main__':
    mode = 0

    macro.end_recording_key = 'alt_l' 
    macro.end_prep_key = 'alt_l'
    macro.terminate_macro_key = 'alt_l'
    macro.use_absolute_coords = True
    macro.keep_initial_delay = False

    if mode == 0:
        record_basic_sequence()

        macro.save_macro('macro.txt')

        '''print('Compressing movements')
        macro.compress_movements(100)

        for i, inp in enumerate(macro.inputs):
            print(f'{i}: {inp}')
        mouse_moves = list(filter(lambda inp: inp.startswith('mouse_move'), macro.inputs))
        print(len(mouse_moves))

        macro.save_macro('compressed_macro.txt')'''

    elif mode == 1:
        sleep(3)

        macro.load_from_file('macro.txt')
        print(f'Initial position: {macro.mouse.position}')
        macro.start_macro(1)
        while macro.executing:
            sleep(0.1)
        print(f'Final position: {macro.mouse.position}')
        print(f'Final win position: {win32api.GetCursorPos()}')