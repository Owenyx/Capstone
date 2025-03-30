from PIL import Image, ImageDraw, ImageFont

def make_3d_key_icon_with_arrow(text, output_path="key_icon_3d.png", size=64,
                                bg_color="#e0e0e0",        # Key background color
                                border_color="#707070",    # Key border color
                                text_color="black",
                                border_width=3, corner_radius=10,
                                arrow_direction="down", padding=10,
                                x_offset=0, y_offset=0,
                                force_font_size=-1):
    """
    Creates a key icon with a 3D drop shadow applied only to the key. The overall image will be of size 'size' x 'size' (default 64),
    with the key scaled to fit inside the padding and shadow. An arrow indicator (either 'down' or 'up') and centered text are drawn
    without shadow.
    
    Args:
        text (str): The text to display inside the key.
        output_path (str): The file path to save the icon.
        size (int): The overall width and height of the image in pixels (default is 64).
        bg_color (str): Background color of the key.
        border_color (str): Color of the key's border.
        text_color (str): Color for the text and arrow.
        border_width (int): The width of the key's border.
        corner_radius (int): The radius of the key's rounded corners.
        arrow_direction (str): "down" or "up" for the arrow direction.
        padding (int): Padding to add around the key.
        x_offset (int): X offset for the key.
        y_offset (int): Y offset for the key.
        force_font_size (int): Force the font size to this value.
    """
    shadow_offset = 4
    if size < 2 * padding + shadow_offset:
        raise ValueError("Size too small for the given padding and shadow offset.")
    key_size = size - 2 * padding - shadow_offset
    margin = border_width // 2
    image = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Define the key rectangle within the padded area (vertical position preserved)
    extra_x = 3
    extra_y = 3.5
    key_rect = [padding + margin, padding + margin, padding + key_size - margin + extra_x, padding + key_size - margin + extra_y]

    draw.rounded_rectangle(key_rect, radius=corner_radius, fill=bg_color,
                           outline=border_color, width=border_width)

    try:
        # Dynamic font sizing
        max_font_size = 30
        min_font_size = 8
        # Use forced font size if specified (not -1)
        if force_font_size > 0:
            font_size = force_font_size
            print(f"Using forced font size: {font_size}")
        else:
            font_size = max_font_size
        
        # Try to load Arial Unicode MS with different possible paths
        possible_font_paths = [
            "arialuni.ttf",                     # Default search
            "C:/Windows/Fonts/arialuni.ttf",    # Windows path
            "/usr/share/fonts/truetype/arialuni.ttf",  # Linux path
            "/Library/Fonts/Arial Unicode.ttf", # macOS path
        ]
        
        font = None
        for font_path in possible_font_paths:
            try:
                font = ImageFont.truetype(font_path, size=font_size)
                print(f"Successfully loaded font: {font_path}")
                break
            except IOError:
                continue
                
        # If Arial Unicode MS isn't available, try other fonts with good Unicode support
        if font is None:
            fallback_fonts = [
                "seguisym.ttf",          # Segoe UI Symbol
                "segoeui.ttf",           # Segoe UI
                "arial.ttf",             # Regular Arial
                "DejaVuSans.ttf",        # DejaVu Sans
                "NotoSans-Regular.ttf",  # Noto Sans
            ]
            
            for fallback in fallback_fonts:
                try:
                    font = ImageFont.truetype(fallback, size=font_size)
                    print(f"Using fallback font: {fallback}")
                    break
                except IOError:
                    continue
        
        # Last resort: default font
        if font is None:
            font = ImageFont.load_default()
            print("WARNING: Using default font - Unicode characters may not display correctly")
        
        # Calculate key width available for text (with some margins)
        key_width = key_rect[2] - key_rect[0]
        max_text_width = key_width * 0.8  # Use 80% of key width as maximum allowed text width
        
        # Check if text fits, if not reduce font size until it does
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        
        # Only perform dynamic sizing if we're not using a forced font size
        while force_font_size <= 0 and text_width > max_text_width and font_size > min_font_size:
            font_size -= 1
            # Try to use the same font that was successful earlier but at smaller size
            try:
                if font._font.filename:  # Access the font filename if possible
                    font = ImageFont.truetype(font._font.filename, size=font_size)
                else:
                    # If we can't get the filename, just use the default at smaller size
                    font = ImageFont.load_default()
            except (AttributeError, IOError):
                font = ImageFont.load_default()
                
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    key_width = key_rect[2] - key_rect[0]
    key_height = key_rect[3] - key_rect[1]
    # Calculate the center position
    text_x = key_rect[0] + (key_width - text_width) / 2 + x_offset
    text_y = key_rect[1] + (key_height - text_height) / 2 + y_offset
    
    # Apply different adjustments based on text length
    text_y -= (font_size - 10) / 2
    
    # Round positions to avoid blurry text from fractional positioning
    text_x = round(text_x)
    text_y = round(text_y)

    draw.text((text_x, text_y), text, fill=text_color, font=font)

    # Use smaller dimensions with odd-numbered width for cleaner triangle rendering
    arrow_width = 14
    arrow_height = 7
    x_center = (key_rect[0] + key_rect[2]) / 2

    # Draw a nicer looking arrow using a filled rectangle with rounded corners
    if arrow_direction.lower() == "down":
        # Place arrow in bottom padding area
        arrow_space_height = size - key_rect[3]
        arrow_y_center = key_rect[3] + arrow_space_height / 2
        
        # Draw triangle arrow
        # Create a cleaner triangle with exact positioning
        # Calculate exact pixel positions for the triangle
        half_width = arrow_width // 2  # Integer division for pixel-perfect alignment
        tip_top = int(arrow_y_center - arrow_height / 2)
        tip_points = [
            (int(x_center) - half_width, tip_top),  # Left point 
            (int(x_center) + half_width, tip_top),  # Right point
            (int(x_center), tip_top + arrow_height)  # Bottom point
        ]
        draw.polygon(tip_points, fill=text_color)
        
    elif arrow_direction.lower() == "up":
        # Place arrow in top padding area
        arrow_space_height = key_rect[1]
        arrow_y_center = arrow_space_height / 2
        
        # Draw triangle arrow
        # Create a cleaner triangle with exact positioning
        # Calculate exact pixel positions for the triangle
        half_width = arrow_width // 2  # Integer division for pixel-perfect alignment
        tip_bottom = int(arrow_y_center + arrow_height / 2)
        tip_points = [
            (int(x_center) - half_width, tip_bottom),  # Left point
            (int(x_center) + half_width, tip_bottom),  # Right point
            (int(x_center), tip_bottom - arrow_height)  # Top point
        ]
        draw.polygon(tip_points, fill=text_color)
    else:
        raise ValueError("Invalid arrow_direction. Use 'down' or 'up'.")

    image.save(output_path)
    print(f"3D key icon saved to {output_path}")

# Add a Unicode character test function at the end of the file
def test_unicode_support():
    """Check if Unicode characters are supported by creating a small test icon."""
    test_chars = [
        ("\u21AA", "Rightwards arrow with hook"),
        ("\u2190", "Leftwards arrow"),
        ("\u2192", "Rightwards arrow"),
        ("\u2191", "Upwards arrow"),
        ("\u2193", "Downwards arrow"),
    ]
    
    print("Testing Unicode character support:")
    for char, name in test_chars:
        print(f"Character: {char} - {name}")
        output_file = f"testIcons/unicode_test_{ord(char):x}.png"
        try:
            make_3d_key_icon_with_arrow(char, output_file, arrow_direction="down")
            print(f"  ✓ Generated test icon: {output_file}")
        except Exception as e:
            print(f"  ✗ Failed to generate icon for {char}: {e}")

if __name__ == "__main__":
    # Uncomment to test Unicode support
    # test_unicode_support()

    icons = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "0",
        "ESC",
        "F1",
        "F2",
        "F3",
        "F4",
        "F5",
        "F6",
        "F7",
        "F8",
        "F9",
        "F10",
        "F11",
        "F12",
        "`",
        "~",
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "&",
        "*",
        "(",
        ")",
        "-",
        "_",
        "=",
        "+",   
        "\u232B",  # Backspace
        "\u21E5", # Tab
        "[",
        '{',
        ']',
        '}',
        '\\',
        '|',
        "CAPS",
        ":",
        ";",
        "'",
        '"',
        "\u21A9",  # Enter
        "\u21E7", # Shift
        ",",
        '<',
        '.',
        '>',
        '/',
        '?',
        "CTRL",
        "Fn",
        "ALT",
        "SPACE",
        "\u2191", # Up
        "\u2193", # Down
        "\u2190", # Left
        "\u2192", # Right
    ]

    for icon in icons:
        iconName = icon.lower()

        color = '#000000'
        x_off = 0.5
        y_off = -1.5
        font_size = -1

        match iconName:
            case "*":
                iconName = "star"
            case '\\':
                iconName = "backslash"
            case "|":
                iconName = 'pipe'
            case '"':
                iconName = 'double_quote'
            case "<":
                iconName = 'less_than'
            case ">":
                iconName = 'greater_than'
            case "/":
                iconName = 'slash'
            case '?':
                iconName = 'question_mark'
            case "\u21E7":
                iconName = 'shift'
                color = '#ffffff'

            case "_":
                y_off -= 10
            case '-':
                y_off -= 6
            case ',':
                y_off -= 10
            case ';':
                x_off += 0.5
                y_off -= 5
            case '.':
                x_off += 0.5
                y_off -= 8
            case "\u2191":
                x_off += 0.5
                y_off -= 0.5
            case "\u2193":
                x_off += 0.5
                y_off -= 0.5
            case "\u2190": # Left
                y_off -= 5
            case "\u2192": # Right
                y_off -= 5
            case "\u2191": # Up
                y_off -= 0.5
            case "\u2193": # Down
                y_off -= 0.5

            case "\u21A9": # Enter
                y_off += 2

            case "\u21E5": # Tab
                y_off -= 5

            case '+':
                y_off -= 4
            case '=':
                y_off -= 5
            case '~':
                y_off -= 7

            case "\u232B": # Backspace
                font_size = 28

            case '$':
                y_off += 2
                x_off += 1

            case _:
                pass

        make_3d_key_icon_with_arrow(icon, f"testIcons/key_press_{iconName}.png", arrow_direction="down",
                                    x_offset=x_off, y_offset=y_off, text_color=color, force_font_size=font_size)
        make_3d_key_icon_with_arrow(icon, f"testIcons/key_release_{iconName}.png", arrow_direction="up",
                                    x_offset=x_off, y_offset=y_off, text_color=color, force_font_size=font_size)