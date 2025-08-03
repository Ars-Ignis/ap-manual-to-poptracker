import os
import shutil

import orjson
from utils import *


def write_json_file(json_object: any, pack_root: str, file_location: str):
    if not os.path.isabs(pack_root):
        raise SyntaxError(f"Pack root must be an absolute path! Given pack root: {pack_root}")
    full_filepath: str = os.path.join(pack_root, file_location)
    if not os.path.exists(os.path.dirname(full_filepath)):
        os.makedirs(os.path.dirname(full_filepath))
    with open(full_filepath, 'wb') as file:
        json_dump = orjson.dumps(json_object, option=orjson.OPT_INDENT_2)
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
        "ScriptHost:LoadScript(\"scripts/logic_common.lua\")\n"
        "ScriptHost:LoadScript(\"scripts/archipelago/archipelago.lua\")\n"
        "Tracker:AddLayouts(\"layouts/options_layout.json\")\n"
        "Tracker:AddLayouts(\"layouts/input_layout.json\")\n"
        "Tracker:AddLayouts(\"layouts/main.json\")\n"
    )
    for location_file_path in location_file_paths:
        file_contents += f"Tracker:AddLocations(\"{location_file_path}\")\n"
    with open(full_filepath, 'w') as file:
        file.write(file_contents)


def write_item_mapping_script(items: list[dict[str, any]], item_name_to_id: dict[str, int], pack_root: str):
    if not os.path.isabs(pack_root):
        raise SyntaxError(f"Pack root must be an absolute path! Given pack root: {pack_root}")
    full_filepath: str = os.path.join(pack_root, "scripts/archipelago/item_mapping.lua")
    if not os.path.exists(os.path.dirname(full_filepath)):
        os.makedirs(os.path.dirname(full_filepath))
    file_content: str = "ITEM_MAPPING = {\n"
    estimated_item_id: int = 1
    for item in items:
        if (("progression" not in item or not item["progression"]) and
           ("progression_skip_balancing" not in item or not item["progression_skip_balancing"])):
            estimated_item_id += 1
            continue
        type: str = "consumable" if "count" in item and int(item["count"]) > 1 else "toggle"
        if item_name_to_id is None:
            file_content += f"    [{estimated_item_id}] = {{\"{to_snake_case(item['name'])}\", \"{type}\"}},\n"
        else:
            file_content += f"    [{item_name_to_id[item['name']]}] = {{\"{to_snake_case(item['name'])}\", \"{type}\"}},\n"
        estimated_item_id += 1
    file_content += "}"
    with open(full_filepath, 'w') as file:
        file.write(file_content)


def write_location_mapping_script(locations: list[dict[str, any]], location_name_to_id: dict[str, int], pack_root: str):
    if not os.path.isabs(pack_root):
        raise SyntaxError(f"Pack root must be an absolute path! Given pack root: {pack_root}")
    full_filepath: str = os.path.join(pack_root, "scripts/archipelago/location_mapping.lua")
    if not os.path.exists(os.path.dirname(full_filepath)):
        os.makedirs(os.path.dirname(full_filepath))
    location_to_id_string: str = "LOCATION_TO_ID_MAP = {\n"
    id_to_location_string: str = "ID_TO_LOCATION_MAP = {\n"
    estimated_location_id: int = 1
    for location in locations:
        section_identifier: str = f"{location['category'][0]}/{location['region']}/{location['name']}/{location['name']}"
        if location_name_to_id is None:
            id_to_location_string += f"    [{estimated_location_id}] = {{\"@{section_identifier}\"}},\n"
            location_to_id_string += f"    [\"{section_identifier}\"] = {estimated_location_id},\n"
        else:
            id_to_location_string += f"    [{location_name_to_id[location['name']]}] = {{\"@{section_identifier}\"}},\n"
            location_to_id_string += f"    [\"{section_identifier}\"] = {location_name_to_id[location['name']]},\n"
        estimated_location_id += 1
    location_to_id_string += "}\n"
    id_to_location_string += "}\n"
    with open(full_filepath, 'w') as file:
        file.write(location_to_id_string + id_to_location_string)


def copy_default_files(items: list[dict[str, any]], options: list[str], pack_root: str):
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
        shutil.copyfile("./data/default_item_option_image.png", item_image_filepath)
    option_images_dirpath: str = os.path.join(pack_root, "images/options/")
    if not os.path.exists(option_images_dirpath):
        os.makedirs(option_images_dirpath)
    for option in options:
        image_filename = f"{option}.png"
        item_image_filepath = os.path.join(option_images_dirpath, image_filename)
        shutil.copyfile("./data/default_item_option_image.png", item_image_filepath)
    ap_lua_filepath = os.path.join(pack_root, "scripts/archipelago/archipelago.lua")
    if not os.path.exists(os.path.dirname(ap_lua_filepath)):
        os.makedirs(os.path.dirname(ap_lua_filepath))
    shutil.copyfile("./data/archipelago.lua", ap_lua_filepath)
    maps_json_filepath = os.path.join(pack_root, "maps/maps.json")
    if not os.path.exists(os.path.dirname(maps_json_filepath)):
        os.makedirs(os.path.dirname(maps_json_filepath))
    shutil.copyfile("./data/maps.json", maps_json_filepath)
    main_layout_json_filepath = os.path.join(pack_root, "layouts/main.json")
    if not os.path.exists(os.path.dirname(main_layout_json_filepath)):
        os.makedirs(os.path.dirname(main_layout_json_filepath))
    shutil.copyfile("./data/main.json", main_layout_json_filepath)
    placeholder_map_image_filepath = os.path.join(pack_root, "images/maps/main.png")
    if not os.path.exists(os.path.dirname(placeholder_map_image_filepath)):
        os.makedirs(os.path.dirname(placeholder_map_image_filepath))
    shutil.copyfile("./data/placeholder_map.png", placeholder_map_image_filepath)


def write_common_lua_scripts(item_groups: dict[str, list[str]], pack_root: str):
    if not os.path.isabs(pack_root):
        raise SyntaxError(f"Pack root must be an absolute path! Given pack root: {pack_root}")
    full_filepath: str = os.path.join(pack_root, "scripts/logic_common.lua")
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
    file_contents += "\n}\n\n"
    has_count_from_group_function: str = """
function has_count_from_group(group_name, count)
    local group_members = ITEM_GROUPS[group_name]
    if group_members == nil then
        return false
    end
    local found_count = 0
    for _, item in pairs(group_members) do
        found_count = found_count + Tracker:ProviderCountForCode(item)
        if found_count >= tonumber(count) then
            return true
        end
    end
    return false
end
    """
    file_contents += has_count_from_group_function
    with open(full_filepath, 'w') as file:
        file.write(file_contents)

