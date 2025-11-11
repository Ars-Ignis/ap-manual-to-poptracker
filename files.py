import os
import shutil

import json
from utils import *


def write_json_file(json_object: any, pack_root: str, file_location: str):
    if not os.path.isabs(pack_root):
        raise SyntaxError(f"Pack root must be an absolute path! Given pack root: {pack_root}")
    full_filepath: str = os.path.join(pack_root, file_location)
    if not os.path.exists(os.path.dirname(full_filepath)):
        os.makedirs(os.path.dirname(full_filepath))
    with open(full_filepath, 'w') as file:
        json_dump = json.dumps(json_object, indent=4)
        file.write(json_dump)


def write_lua_init_file(location_file_paths: list[str], pack_root: str):
    if not os.path.isabs(pack_root):
        raise SyntaxError(f"Pack root must be an absolute path! Given pack root: {pack_root}")
    full_filepath: str = os.path.join(pack_root, "scripts/init.lua")
    if not os.path.exists(os.path.dirname(full_filepath)):
        os.makedirs(os.path.dirname(full_filepath))
    file_contents: str = (
        "Tracker:AddItems(\"items/items.json\")\n"
        "Tracker:AddItems(\"items/options.json\")\n"
        "Tracker:AddMaps(\"maps/maps.json\")\n"
        "ScriptHost:LoadScript(\"scripts/item_groups.lua\")\n"
        "ScriptHost:LoadScript(\"scripts/util.lua\")\n"
        "ScriptHost:LoadScript(\"scripts/archipelago/archipelago.lua\")\n"
        "Tracker:AddLayouts(\"layouts/options_layout.json\")\n"
        "Tracker:AddLayouts(\"layouts/input_layout.json\")\n"
        "Tracker:AddLayouts(\"layouts/map_layouts.json\")\n"
        "Tracker:AddLayouts(\"layouts/main.json\")\n"
    )
    for location_file_path in location_file_paths:
        file_contents += f"Tracker:AddLocations(\"{location_file_path}\")\n"
    with open(full_filepath, 'w') as file:
        file.write(file_contents)


def write_item_mapping_script(items: list[dict[str, any]],
                              starting_index: int,
                              item_name_to_id: dict[str, int],
                              pack_root: str):
    if not os.path.isabs(pack_root):
        raise SyntaxError(f"Pack root must be an absolute path! Given pack root: {pack_root}")
    full_filepath: str = os.path.join(pack_root, "scripts/archipelago/item_mapping.lua")
    if not os.path.exists(os.path.dirname(full_filepath)):
        os.makedirs(os.path.dirname(full_filepath))
    file_content: str = "ITEM_MAPPING = {\n"
    calculated_item_id: int = starting_index
    for item in items:
        if "id" in item and item["id"] > calculated_item_id:
            calculated_item_id = item["id"]
        if (("progression" in item and item["progression"]) or
           ("progression_skip_balancing" in item and item["progression_skip_balancing"])):
            item_type: str = "consumable" if "count" in item and int(item["count"]) > 1 else "toggle"
            if item_name_to_id is None:
                file_content += \
                    f"    [{calculated_item_id}] = {{\"{to_snake_case(item['name'])}\", \"{item_type}\"}},\n"
            else:
                file_content += \
                    f"    [{item_name_to_id[item['name']]}] = {{\"{to_snake_case(item['name'])}\", \"{item_type}\"}},\n"
        calculated_item_id += 1
    file_content += "}"
    with open(full_filepath, 'w') as file:
        file.write(file_content)


def write_location_mapping_script(locations: list[dict[str, any]],
                                  starting_index: int,
                                  location_name_to_id: dict[str, int],
                                  pack_root: str):
    if not os.path.isabs(pack_root):
        raise SyntaxError(f"Pack root must be an absolute path! Given pack root: {pack_root}")
    full_filepath: str = os.path.join(pack_root, "scripts/archipelago/location_mapping.lua")
    if not os.path.exists(os.path.dirname(full_filepath)):
        os.makedirs(os.path.dirname(full_filepath))
    location_to_id_string: str = "LOCATION_TO_ID_MAP = {\n"
    id_to_location_string: str = "ID_TO_LOCATION_MAP = {\n"
    calculated_location_id: int = starting_index
    for location in locations:
        if "id" in location and location["id"] > calculated_location_id:
            calculated_location_id = location["id"]
        section_identifier: str = f"{location['category'][0]}/{location['region']}/{location['name']}"
        if location_name_to_id is None:
            id_to_location_string += f"    [{calculated_location_id}] = {{\"@{section_identifier}\"}},\n"
            location_to_id_string += f"    [\"{section_identifier}\"] = {calculated_location_id},\n"
        else:
            id_to_location_string += f"    [{location_name_to_id[location['name']]}] = {{\"@{section_identifier}\"}},\n"
            location_to_id_string += f"    [\"{section_identifier}\"] = {location_name_to_id[location['name']]},\n"
        calculated_location_id += 1
    location_to_id_string += "}\n"
    id_to_location_string += "}\n"
    with open(full_filepath, 'w') as file:
        file.write(location_to_id_string + id_to_location_string)


def copy_default_files(items: list[dict[str, any]], options: list[str], map_names: set[str], pack_root: str):
    if not os.path.isabs(pack_root):
        raise SyntaxError(f"Pack root must be an absolute path! Given pack root: {pack_root}")
    item_images_dirpath: str = os.path.join(pack_root, "images/items/")
    if not os.path.exists(item_images_dirpath):
        os.makedirs(item_images_dirpath)
    for item in items:
        if (("progression" not in item or not item["progression"]) and
           ("progression_skip_balancing" not in item or not item["progression_skip_balancing"])):
            continue
        image_filename = f"{to_snake_case(item['name'])}.png"
        item_image_filepath = os.path.join(item_images_dirpath, image_filename)
        if not os.path.exists(item_image_filepath):
            shutil.copyfile("./data/default_item_option_image.png", item_image_filepath)
    option_images_dirpath: str = os.path.join(pack_root, "images/options/")
    if not os.path.exists(option_images_dirpath):
        os.makedirs(option_images_dirpath)
    for option in options:
        image_filename = f"{option}.png"
        item_image_filepath = os.path.join(option_images_dirpath, image_filename)
        if not os.path.exists(item_image_filepath):
            shutil.copyfile("./data/default_item_option_image.png", item_image_filepath)
    ap_lua_filepath = os.path.join(pack_root, "scripts/archipelago/archipelago.lua")
    if not os.path.exists(os.path.dirname(ap_lua_filepath)):
        os.makedirs(os.path.dirname(ap_lua_filepath))
    shutil.copyfile("./data/archipelago.lua", ap_lua_filepath)
    util_lua_filepath = os.path.join(pack_root, "scripts/util.lua")
    if not os.path.exists(os.path.dirname(util_lua_filepath)):
        os.makedirs(os.path.dirname(util_lua_filepath))
    shutil.copyfile("./data/util.lua", util_lua_filepath)
    main_layout_json_filepath = os.path.join(pack_root, "layouts/main.json")
    if not os.path.exists(os.path.dirname(main_layout_json_filepath)):
        os.makedirs(os.path.dirname(main_layout_json_filepath))
    shutil.copyfile("./data/main.json", main_layout_json_filepath)
    for map_name in sorted(list(map_names)):
        placeholder_map_image_filepath = os.path.join(pack_root, f"images/maps/{map_name}.png")
        if not os.path.exists(os.path.dirname(placeholder_map_image_filepath)):
            os.makedirs(os.path.dirname(placeholder_map_image_filepath))
        if not os.path.exists(placeholder_map_image_filepath):
            shutil.copyfile("./data/placeholder_map.png", placeholder_map_image_filepath)


def write_item_group_lua_scripts(item_groups: dict[str, list[str]], pack_root: str):
    if not os.path.isabs(pack_root):
        raise SyntaxError(f"Pack root must be an absolute path! Given pack root: {pack_root}")
    full_filepath: str = os.path.join(pack_root, "scripts/item_groups.lua")
    if not os.path.exists(os.path.dirname(full_filepath)):
        os.makedirs(os.path.dirname(full_filepath))
    file_contents: str = "ITEM_GROUPS = {\n"
    first_group: bool = True
    for group, items in item_groups.items():
        if first_group:
            first_group = False
        else:
            file_contents += ",\n"
        file_contents += f"    [\"{group}\"] = {{"
        first_item: bool = True
        for item in items:
            if first_item:
                first_item = False
            else:
                file_contents += ", "
            file_contents += f"\"{to_snake_case(item)}\""
        file_contents += "}"
    file_contents += "\n}\n"
    with open(full_filepath, 'w') as file:
        file.write(file_contents)

