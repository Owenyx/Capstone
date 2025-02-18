from pynput import keyboard, mouse
from pynput.keyboard import Key, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController

# 1. KEYBOARD MONITORING
def on_press(key):
    try:
        print(f'Alphanumeric key pressed: {key.char}')
    except AttributeError:
        print(f'Special key pressed: {key}')

def on_release(key):
    print(f'Key released: {key}')
    if key == Key.esc:  # Stop listener on ESC
        return False

# Start keyboard listener
keyboard_listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)
keyboard_listener.start()

# 2. MOUSE MONITORING
def on_move(x, y):
    print(f'Mouse moved to ({x}, {y})')

def on_click(x, y, button, pressed):
    action = 'Pressed' if pressed else 'Released'
    print(f'{action} {button} at ({x}, {y})')

def on_scroll(x, y, dx, dy):
    direction = 'down' if dy < 0 else 'up'
    print(f'Scrolled {direction} at ({x}, {y})')

# Start mouse listener
mouse_listener = mouse.Listener(
    on_move=on_move,
    on_click=on_click,
    on_scroll=on_scroll
)
mouse_listener.start()

# 3. KEYBOARD CONTROL
keyboard_ctrl = KeyboardController()

# Type a character
keyboard_ctrl.press('a')
keyboard_ctrl.release('a')

# Type a string
keyboard_ctrl.type('Hello, World!')

# Press special keys
keyboard_ctrl.press(Key.shift)
keyboard_ctrl.press('a')
keyboard_ctrl.release('a')
keyboard_ctrl.release(Key.shift)

# Special key combinations
with keyboard_ctrl.pressed(Key.ctrl):
    keyboard_ctrl.press('c')
    keyboard_ctrl.release('c')

# 4. MOUSE CONTROL
mouse_ctrl = MouseController()

# Get current position
print(mouse_ctrl.position)

# Move mouse (absolute)
mouse_ctrl.position = (100, 200)

# Move mouse (relative)
mouse_ctrl.move(50, 0)  # Move 50 pixels right

# Click
mouse_ctrl.press(Button.left)
mouse_ctrl.release(Button.left)

# Double click
mouse_ctrl.click(Button.left, 2)

# Scroll
mouse_ctrl.scroll(0, 2)  # Scroll up 2 units
mouse_ctrl.scroll(0, -2) # Scroll down 2 units

# 5. AVAILABLE SPECIAL KEYS
"""
Key.alt
Key.alt_l
Key.alt_r
Key.alt_gr
Key.backspace
Key.caps_lock
Key.cmd
Key.cmd_l
Key.cmd_r
Key.ctrl
Key.ctrl_l
Key.ctrl_r
Key.delete
Key.down
Key.end
Key.enter
Key.esc
Key.f1 (through f20)
Key.home
Key.insert
Key.left
Key.menu
Key.num_lock
Key.page_down
Key.page_up
Key.pause
Key.print_screen
Key.right
Key.scroll_lock
Key.shift
Key.shift_l
Key.shift_r
Key.space
Key.tab
Key.up
"""

# 6. MOUSE BUTTONS
"""
Button.left
Button.right
Button.middle
Button.button8
Button.button9
"""

# 7. EXAMPLE: COMPLETE MONITORING SCRIPT
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

# Run the monitoring
if __name__ == '__main__':
    monitor_input()