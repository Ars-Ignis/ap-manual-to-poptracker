

OPTION_ROW_SIZE = 4
OPTION_ITEM_WIDTH = 40
OPTION_ITEM_HEIGHT = 40
OPTION_ITEM_MARGIN = 10


def build_option_items(options: set[str]) -> list[dict[str, any]]:
    output_data: list[dict[str, any]] = []
    for option in sorted(options):
        option_dict: dict[str, any] = {
            "name": option,
            "type": "toggle",
            "img": f"images/options/{option}.png",
            "loop": True,
            "codes": option
        }
        output_data.append(option_dict)
    return output_data


def build_option_layout(options: set[str]) -> dict[str, any]:
    rows: list[list[str]] = []
    options_list: list[str] = sorted(options)
    for i in range((len(options_list)//OPTION_ROW_SIZE)+1):
        row: list[str] = []
        for option in options_list[i*OPTION_ROW_SIZE:(i+1)*OPTION_ROW_SIZE]:
            row.append(option)
        while len(row) < OPTION_ROW_SIZE:
            row.append("")
        rows.append(row)
    content: dict[str, any] = {
        "type": "itemgrid",
        "item_width": OPTION_ITEM_WIDTH,
        "item_height": OPTION_ITEM_HEIGHT,
        "v_alignment": "center",
        "h_alignment": "center",
        "dropshadow": False,
        "margin": OPTION_ITEM_MARGIN,
        "rows": rows
    }
    settings_popup: dict[str, any] = {
        "type": "array",
        "orientation": "horizontal",
        "v_alignment": "top",
        "min_width": (OPTION_ROW_SIZE * (OPTION_ITEM_WIDTH + OPTION_ITEM_MARGIN)) - OPTION_ITEM_MARGIN,
        "min_height": (((len(options_list) // OPTION_ROW_SIZE) + 1) * (OPTION_ITEM_HEIGHT + OPTION_ITEM_MARGIN)) - OPTION_ITEM_MARGIN,
        "content": content
    }
    return {"settings_popup": settings_popup}
