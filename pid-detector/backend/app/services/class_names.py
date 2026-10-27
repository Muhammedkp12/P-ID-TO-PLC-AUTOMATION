# class_N in the model = Symbol (N+1) in Figure 3 of arXiv 2109.03794
# Each entry is (name, sure). sure=False means named from the shape only.
CLASS_NAMES = {
    0: ("gate_valve", False),            # Symbol 1, plain bowtie
    1: ("globe_valve", False),           # Symbol 2, bowtie with open circle
    2: ("globe_valve_solid", False),     # Symbol 3, bowtie with filled circle
    3: ("valve_outline", False),         # Symbol 4, hollow bowtie
    4: ("ball_valve", False),            # Symbol 5, bowtie with small circle
    5: ("plug_valve", False),            # Symbol 6
    6: ("valve_with_stem", False),       # Symbol 7
    7: ("check_valve", False),           # Symbol 8, triangle with bar
    8: ("diaphragm_valve", False),       # Symbol 9, curved bowtie
    9: ("valve_actuated", False),        # Symbol 10, filled marker on top
    10: ("valve_half_filled", False),    # Symbol 11
    11: ("valve_closed", False),         # Symbol 12, filled bowtie
    12: ("globe_valve_closed", False),   # Symbol 13, filled with circle
    13: ("control_valve", True),         # Symbol 14, dome actuator
    14: ("inline_device_open", False),   # Symbol 15, open circle inline
    15: ("inline_device_filled", False), # Symbol 16, filled circle inline
    16: ("flanged_item_1", False),       # Symbol 17
    17: ("flanged_item_2", False),       # Symbol 18
    18: ("flanged_item_3", False),       # Symbol 19
    19: ("reducer", True),               # Symbol 20, trapezoid
    20: ("flange", False),               # Symbol 21, two parallel bars
    21: ("coil_or_exchanger", False),    # Symbol 22, zigzag box
    22: ("jacketed_pipe", False),        # Symbol 23, dashed tube
    23: ("flow_arrow", True),            # Symbol 24, arrow on line
    24: ("circle_x", False),             # Symbol 25, circle with X
    25: ("instrument_bubble", True),     # Symbol 26, circle with text
    26: ("instrument_bubble", True),     # Symbol 27
    27: ("instrument_bubble", True),     # Symbol 28
    28: ("instrument_bubble_line", True),# Symbol 29, circle with center line
    29: ("instrument_square", False),    # Symbol 30, square with text
    30: ("instrument_in_square", False), # Symbol 31, circle inside square
    31: ("label_box", False),            # Symbol 32, box with 3 text lines
}


def class_label(cls):
    """Turn 'class_30' into a readable name. Adds '?' when unsure."""
    try:
        n = int(str(cls).split("_")[-1])
    except ValueError:
        return str(cls)
    name, sure = CLASS_NAMES.get(n, (None, False))
    if not name:
        return str(cls)
    return name if sure else name + "?"