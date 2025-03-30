
'''
Notes:

Keys:
Each png should of course have the key_press_ or key_release_ prefix.


Case:
All individual letter keys should be made lowercase before getting the icon. Leave all other inputs with original case.


Equivalence:
alt_l and alt_gr both map to alt.png
shift and shift_r both map to shift.png
ctrl_l and ctrl_r both map to ctrl.png

^^^ Nothing there was a typo, the names are just a bit odd.


Other mappings due to the characters not being allowed in file names:
? = question_mark.png
" = double_quote.png
* = star.png
\ = backslash.png
| = pipe.png
< = less_than.png
> = greater_than.png
/ = slash.png


Unknown:
I covered all mappings on my keyboard, but to be safe, map any key that isn't accounted for to key_press_unknown.png or key_release_unknown.png


Mouse:

Movements:
Take the form of:
mouse_move_x_y_to_x_y
all movements should map to mouse_move.png


Side buttons:

They take the form of:
mouse_press_Button.x1
mouse_press_Button.x2
so on...

They should all map to mouse_press_Button.x.png or mouse_release_Button.x.png

To be clear, x is not a variable, it is actually part of the string and png name.
'''