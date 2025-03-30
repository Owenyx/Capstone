from PIL import Image, ImageDraw, ImageFont

def make_3d_key_icon_with_arrow(text, output_path="key_icon_3d.png", size=64,
                                bg_color="#e0e0e0",        # Key background color
                                border_color="#707070",    # Key border color
                                text_color="black",
                                border_width=3, corner_radius=10,
                                arrow_direction="down", padding=10):
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
        max_font_size = 20
        min_font_size = 8
        font_size = max_font_size
        font = ImageFont.truetype("arialuni.ttf", size=font_size)
        
        # Calculate key width available for text (with some margins)
        key_width = key_rect[2] - key_rect[0]
        max_text_width = key_width * 0.8  # Use 80% of key width as maximum allowed text width
        
        # Check if text fits, if not reduce font size until it does
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        
        while text_width > max_text_width and font_size > min_font_size:
            font_size -= 1
            font = ImageFont.truetype("arialuni.ttf", size=font_size)
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
    text_x = key_rect[0] + (key_width - text_width) / 2 + 1
    text_y = key_rect[1] + (key_height - text_height) / 2
    
    # Apply different adjustments based on text length
    text_y -= (font_size - 10) / 2 - (font_size // 20)
    
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

if __name__ == "__main__":

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
        "\u21AA",  # Unicode rightwards arrow with hook ↪
        "Backspace",
    ]

    # Generate a key icon with a down arrow
    make_3d_key_icon_with_arrow("A", "testIcons/key_icon_3d_down.png", arrow_direction="down")
    # Generate a key icon with an up arrow
    make_3d_key_icon_with_arrow("A", "testIcons/key_icon_3d_up.png", arrow_direction="up")

    # Generate a key icon with a down arrow
    make_3d_key_icon_with_arrow("CTRL", "testIcons/key_icon_3d_ctrl_down.png", arrow_direction="down")
    # Generate a key icon with an up arrow
    make_3d_key_icon_with_arrow("CTRL", "testIcons/key_icon_3d_ctrl_up.png", arrow_direction="up")

    # Generate a key icon with a down arrow
    make_3d_key_icon_with_arrow("ALT", "testIcons/key_icon_3d_alt_down.png", arrow_direction="down")
    # Generate a key icon with an up arrow
    make_3d_key_icon_with_arrow("ALT", "testIcons/key_icon_3d_alt_up.png", arrow_direction="up")

    # Generate a key icon with a down arrow
    make_3d_key_icon_with_arrow("\u21AA", "testIcons/key_icon_3d_arrow_hook_down.png", arrow_direction="down")
    # Generate a key icon with an up arrow
    make_3d_key_icon_with_arrow("\u21AA", "testIcons/key_icon_3d_arrow_hook_up.png", arrow_direction="up")

    # Helper function to convert Unicode code points to characters
    def unicode_to_char(code_point):
        """Convert a Unicode code point in U+XXXX format to the actual character"""
        if code_point.startswith("U+"):
            hex_value = code_point[2:]  # Remove the "U+" prefix
            return chr(int(hex_value, 16))
        return code_point

    # Examples of other Unicode arrow characters:
    # make_3d_key_icon_with_arrow("\u2190", "testIcons/key_icon_3d_arrow_left.png", arrow_direction="down")  # ←
    # make_3d_key_icon_with_arrow("\u2192", "testIcons/key_icon_3d_arrow_right.png", arrow_direction="down") # →
    # make_3d_key_icon_with_arrow("\u2191", "testIcons/key_icon_3d_arrow_up.png", arrow_direction="down")    # ↑
    # make_3d_key_icon_with_arrow("\u2193", "testIcons/key_icon_3d_arrow_down.png", arrow_direction="down")  # ↓

    
    