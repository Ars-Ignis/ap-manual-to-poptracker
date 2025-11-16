from utils import *

OPTION_ROW_SIZE = 4
OPTION_ITEM_WIDTH = 40
OPTION_ITEM_HEIGHT = 40
OPTION_ITEM_MARGIN = 10


def build_option_items(options_json: dict[str, any], category_options: set[str]) -> list[dict[str, any]]:
    output_data: list[dict[str, any]] = []
    for category_option in sorted(category_options):
        category_option_dict: dict[str, any] = {
            "name": format_to_valid_identifier(category_option),
            "type": "toggle",
            "img": f"images/options/{category_option}.png",
            "loop": True,
            "codes": category_option
        }
        output_data.append(category_option_dict)
    if "user" in options_json:
        user_options: dict[str, any] = options_json["user"]
        for user_option_name, user_option_data in user_options.items():
            user_option_type: str = user_option_data["type"].title()
            valid_name: str = format_to_valid_identifier(user_option_name)
            user_option_dict: dict[str, any] = {
                "name": valid_name,
                "loop": True,
                "codes": valid_name
            }
            if user_option_type == "Toggle":
                user_option_dict["type"] = "toggle"
                user_option_dict["img"] = f"images/options/{valid_name}.png"
            elif user_option_type == "Range":
                user_option_dict["type"] = "consumable"
                user_option_dict["img"] = f"images/options/{valid_name}.png"
                user_option_dict["min_quantity"] = user_option_data["range_start"] if "range_start" in user_option_data else 0
                user_option_dict["max_quantity"] = user_option_data["range_end"] if "range_end" in user_option_data else 1
            elif user_option_type == "Choice":
                if "allow_custom_value" in user_option_dict and user_option_dict["allow_custom_value"]:
                    print(f"WARNING! User Choice option {user_option_name} allows custom values! There's no way to "
                          f"reasonably model that in PopTracker, so skipping this option.")
                    continue
                user_option_dict["inherit_codes"] = False
                user_option_dict["type"] = "progressive"
                user_option_dict["allow_disabled"] = False
                stages_list: list[dict[str, any]] = []
                for choice_name, choice_value in user_option_data["values"]:
                    valid_choice_name: str = format_to_valid_identifier(choice_name)
                    choice_code: str = f"{valid_name}_{valid_choice_name}"
                    stage_dict: dict[str, any] = {
                        "img": f"images/options/{choice_code}.png",
                        "codes": choice_code,
                        "inherit_codes": False,
                        "name": choice_name
                    }
                    stages_list.append(stage_dict)
                user_option_dict["stages"] = stages_list
            else:
                print(f"WARNING! Unrecognized option type {user_option_type} for option {user_option_name}! Ignoring "
                      f"this option.")
                continue
            output_data.append(user_option_dict)
    return output_data


def build_option_layout(options: list[dict[str, any]]) -> dict[str, any]:
    rows: list[list[str]] = []
    options_list: list[str] = [option["name"] for option in options]
    for i in range((len(options_list)//OPTION_ROW_SIZE)+1):
        row: list[str] = []
        for option_name in options_list[i*OPTION_ROW_SIZE:(i+1)*OPTION_ROW_SIZE]:
            row.append(option_name)
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
