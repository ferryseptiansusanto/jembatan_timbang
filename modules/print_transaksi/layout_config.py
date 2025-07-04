# modules/print_transaksi/layout_config.py

SLIP_PROFILES = {
    "A6": {
        "width_mm": 105,
        "height_mm": 148,
        "margin": {
            "left": 10,
            "right": 10,
            "top": 10,
            "bottom": 10
        }
    },
    "A5": {
        "width_mm": 148,
        "height_mm": 210,
        "margin": {
            "left": 15,
            "right": 15,
            "top": 10,
            "bottom": 10
        }
    },
    "POS80": {
        "width_mm": 80,
        "height_mm": 200,
        "margin": {
            "left": 5,
            "right": 5,
            "top": 5,
            "bottom": 5
        }
    }
}

def get_slip_layout(profile_name="A6"):
    layout = SLIP_PROFILES.get(profile_name, SLIP_PROFILES["A6"])
    return layout["width_mm"], layout["height_mm"], layout["margin"]