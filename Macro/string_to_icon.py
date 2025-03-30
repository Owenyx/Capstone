# This map only contains icons for keys that were in the icon set we used
# Icon author: https://www.flaticon.com/authors/littleicon
symbol_to_word = {
    "*": "star",
    "\\": "backslash",
    "/": "slash",
    "|": "pipe",
    "<": "less_than",
    ">": "greater_than",
    "?": "question_mark",
    '"': "double_quote",
}

def string_to_macro_icon(input):
    # Convert all inputs to lowercase before using
    if input.lower() in icon_map:
        icon_string = icon_map[input.lower()]
    else:
        icon_string = 'unknown'

    icon_string += '.png'
    
    return tk.PhotoImage(file=f"Macro Icons/{icon_string}")


'''
Notes:

Case:
All individual letter keys should be made lowercase before getting the icon. Leave all other inputs with original case.

Equivalence:
alt_l and alt_gr both map to alt.png
shift and shift_r both map to shift.png
ctrl_l and ctrl_r both map to ctrl.png

Invalid:
? = question_mark.png
" = double_quote.png
* = star.png
\ = backslash.png
| = pipe.png
< = less_than.png
> = greater_than.png
/ = slash.png


'''