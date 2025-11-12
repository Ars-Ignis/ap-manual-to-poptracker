import argparse
import zipfile as zip
from items import *
from locations import *
from files import *
from utils import *
from options import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manual APWorld to PopTracker Pack converter.")
    parser.add_argument("apworld_path", help="The full path to the Manual APWorld you want to convert.")
    parser.add_argument("--output_path", help="The output directory to build the PopTracker pack in. If not provided, "
                                              "will default to a folder named poptracker in the directory containing the"
                                              " APWorld.")
    parser.add_argument("--datapackage_URL", help="URL for finding location and item IDs; will be estimated if not "
                                                  "provided")
    parser.add_argument("--author", help="The name to use as the author of the PopTracker pack")
    args = parser.parse_args()
    if not os.path.isabs(args.apworld_path):
        print(f"Path is not an absolute path! {args.apworld_path}")
        exit(0)
    # Confirm the .apworld path is correct, and points to a zip file
    if not zip.is_zipfile(args.apworld_path):
        print(f"Path does not point to a valid zip file! {args.apworld_path}")
        exit(0)
    apworld_name: str = os.path.splitext(os.path.basename(args.apworld_path))[0]
    if not args.output_path:
        apworld_dir: str = os.path.split(args.apworld_path)[0]
        args.output_path = os.path.join(apworld_dir, "poptracker")
    # Read and parse the relevant JSON files
    with zip.ZipFile(args.apworld_path) as apworld:
        items_json = apworld.read(f"{apworld_name}/data/items.json").decode("utf-8")
        locations_json = apworld.read(f"{apworld_name}/data/locations.json").decode("utf-8")
        regions_json = apworld.read(f"{apworld_name}/data/regions.json").decode("utf-8")
        categories_json = apworld.read(f"{apworld_name}/data/categories.json").decode("utf-8")
        game_json = apworld.read(f"{apworld_name}/data/game.json").decode("utf-8")
        items = json.loads(items_json)
        locations = json.loads(locations_json)
        regions = json.loads(regions_json)
        categories = json.loads(categories_json)
        game = json.loads(game_json)

    for location in locations:
        if "region" not in location:
            location["region"] = "__start__"

    poptracker_items: list[dict[str, any]]
    item_values: dict[str, dict[str, int]]
    poptracker_items, item_values = parse_items(items)
    item_groups: dict[str, list[str]] = get_item_groups(items)
    input_layout: list[dict[str, any]] = build_item_layout(item_groups, 10)
    write_json_file(poptracker_items, args.output_path, "items/items.json")
    write_json_file(input_layout, args.output_path, "layouts/input_layout.json")

    region_graph: dict[str, list[str]] = build_region_graph(regions)
    regions["__start__"] = {}
    grouped_locations: dict[str, list[dict[str, any]]] = group_locations_by_key("category", locations)

    visibility_options: dict[str, list[str]] = {}
    poptracker_options: set[str] = set()
    for category, category_data in categories.items():
        if "yaml_option" in category_data:
            visibility_options[category] = []
            for option_name in category_data["yaml_option"]:
                visibility_options[category].append(option_name)
                poptracker_options.add(option_name.lstrip("!"))

    poptracker_option_items: list[dict[str, any]] = build_option_items(poptracker_options)
    write_json_file(poptracker_option_items, args.output_path, "items/options.json")
    poptracker_option_layout: dict[str, any] = build_option_layout(poptracker_options)
    write_json_file(poptracker_option_layout, args.output_path, "layouts/options_layout.json")

    total_square_count: int = 0
    locations_file_paths: list[str] = []
    map_names: set[str] = set()
    functions: dict[str, int] = {}
    for group, locations_in_group in grouped_locations.items():
        total_square_count, new_map_names, poptracker_locations, new_functions = \
            build_locations_json(locations_in_group, regions, region_graph, item_groups, visibility_options,
                                 total_square_count, group)
        locations_file_path: str = f"locations/{to_snake_case(group)}.json"
        locations_file_paths.append(locations_file_path)
        write_json_file(poptracker_locations, args.output_path, locations_file_path)
        map_names |= new_map_names
        functions |= new_functions
    poptracker_maps: list[dict[str, any]] = build_maps_json(map_names)
    write_json_file(poptracker_maps, args.output_path, "maps/maps.json")
    poptracker_map_layouts: dict[str, any] = build_map_tabs_layout(map_names)
    write_json_file(poptracker_map_layouts, args.output_path, "layouts/map_layouts.json")

    if len(functions) > 0:
        write_custom_util_lua_file(functions, args.output_path)
    write_lua_init_file(locations_file_paths, len(functions) > 0, args.output_path)

    game_name: str = f"Manual_{game['game']}_{game['creator']}"

    item_name_to_id = None
    location_name_to_id = None
    if args.datapackage_URL:
        try:
            import requests
            try:
                games_dict: dict[str, any] = requests.get(args.datapackage_URL).json()["games"]
                if game_name in games_dict:
                    item_name_to_id: dict[str, int] = games_dict[game_name]["item_name_to_id"]
                    location_name_to_id: dict[str, int] = games_dict[game_name]["location_name_to_id"]
                else:
                    print(f"Warning! The datapackage at {args.datapackage_URL} does not contain an entry for game "
                          f"{game_name}. Are you sure your world is running on that web host? Continuing with "
                          f"estimated item and location IDs.")
            except requests.exceptions.RequestException:
                print(f"Warning! could not reach and read the datapackage at {args.datapackage_URL}. Continuing with "
                      f"estimated item and location IDs.")
        except ImportError:
            print("Warning! You are trying to use a datapackage URL without the requests module installed. " 
                  "Continuing with estimated item and location IDs.  Please run \"pip install requests\" and "
                  "try again if you need IDs from the datapackage.")
    starting_index: int = game["starting_index"] if "starting_index" in game else 0
    write_data_lua_script(item_groups, item_values, args.output_path)
    write_item_mapping_script(items, starting_index, item_name_to_id, args.output_path)
    write_location_mapping_script(locations, starting_index, location_name_to_id, args.output_path)
    copy_default_files(items, poptracker_options, map_names, args.output_path)

    tracker_json_object: dict[str, any] = {"display_name": "Map Tracker", "flags": ["ap", "apmanual"]}
    variants_json_object: dict[str, any] = {"tracker": tracker_json_object}
    manifest_json_object: dict[str, any] = {
        "name": f"{game['game']} for Archipelago (Manual)",
        "game_name": game_name,
        "package_version": "1.0.0",
        "package_uid": f"Manual_{game['game']}_{game['creator']}",
        "variants": variants_json_object
    }
    if args.author:
        manifest_json_object["author"] = args.author
    write_json_file(manifest_json_object, args.output_path, "manifest.json")

    if functions:
        print("========================================================")
        print("| WARNING! You have custom logic hooks in your logic!  |")
        print("| You will need to fill out the function stubs in      |")
        print("| scripts/custom_util.lua with your custom logic for   |")
        print("| your pack to work correctly!                         |")
        print("|                                                      |")
        print("| Custom functions found:                              |")
        for function_name in sorted(functions.keys()):
            log_line: str = f"| -{function_name}".ljust(54) + " |"
            print(log_line)
        print("========================================================")
    print(f"\nAll done! Your PopTracker pack is located at {args.output_path}")
