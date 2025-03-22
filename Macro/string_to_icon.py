# This map only contains icons for keys that were in the icon set we used
# Icon author: https://www.flaticon.com/authors/littleicon
icon_map = {
    'key_press_a': 'letter-a',
    'key_press_b': 'letter-b',
    'key_press_c': 'letter-c',
    'key_press_d': 'letter-d',
    'key_press_e': 'letter-e',
    'key_press_f': 'letter-f',
    'key_press_g': 'letter-g',
    'key_press_h': 'letter-h',
    'key_press_i': 'letter-i',
    'key_press_j': 'letter-j',
    'key_press_k': 'letter-k',
    'key_press_l': 'letter-l',
    'key_press_m': 'letter-m',
    'key_press_n': 'letter-n',
    'key_press_o': 'letter-o',
    'key_press_p': 'letter-p',
    'key_press_q': 'letter-q',
    'key_press_r': 'letter-r',
    'key_press_s': 'letter-s',
    'key_press_t': 'letter-t',
    'key_press_u': 'letter-u',
    'key_press_v': 'letter-v',
    'key_press_w': 'letter-w',
    'key_press_x': 'letter-x',
    'key_press_y': 'letter-y',
    'key_press_z': 'letter-z',
    'key_press_0': 'number-0',
    'key_press_1': 'number-1',
    'key_press_2': 'number-2',
    'key_press_3': 'number-3',
    'key_press_4': 'number-4',
    'key_press_5': 'number-5', 
    'key_press_6': 'number-6',
    'key_press_7': 'number-7',
    'key_press_8': 'number-8',
    'key_press_9': 'number-9',
    'key_press_space': 'space',
    'key_press_backspace': 'backspace',
    'key_press_tab': 'tab',
    'key_press_enter': 'enter',
    'key_press_esc': 'escape',
    'key_press_shift_l': 'shift',
    'key_press_shift_r': 'shift',
    'key_press_ctrl_l': 'ctrl',
    'key_press_ctrl_r': 'ctrl',
    'key_press_alt_l': 'alt',
    'key_press_alt_gr': 'alt',
    'key_press_+': 'plus',
    'key_press_-': 'minus',
    'key_press_*': 'asterisk',
    'key_press_=': 'equal',
    'key_press_[': 'open-bracket',
    'key_press_]': 'close-bracket',
    'key_press_/': 'slash',
    'key_press_\\': 'backslash',
    'key_press_!': 'exclamation-mark',
    'key_press_@': 'at',
    'key_press_#': 'hash',
    'key_press_down': 'down-arrow',
    'key_press_up': 'up-arrow',
    'key_press_left': 'left-arrow',
    'key_press_right': 'right-arrow',
    'mouse_press_Button.left': 'left-click',
    'mouse_press_Button.right': 'right-click',
    'mouse_press_Button.middle': 'middle-click',
    # Scroll up and down icons are added, but they need to be mapped in a special way
    # So for now we'll use the general scroll icon for both
    'mouse_scroll_up': 'scroll',
    'mouse_scroll_down': 'scroll', 
    'mouse_move': 'move',
}

def string_to_macro_icon(input):
    # Convert all inputs to lowercase before using
    if input.lower() in icon_map:
        icon_string = icon_map[input.lower()]
    else:
        icon_string = 'unknown'

    icon_string += '.png'
    
    return tk.PhotoImage(file=f"Macro Icons/{icon_string}")