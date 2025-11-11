from logic import *


LOCATION_ROW_SIZE = 20
LOCATION_SPACING = 25


def build_region_graph(regions: dict[str, any]) -> dict[str, list[str]]:
    region_graph: dict[str, list[str]] = {"__start__": []}
    for region, region_data in regions.items():
        if "connects_to" in region_data and region_data["connects_to"]:
            region_graph[region] = region_data["connects_to"]
        else:
            region_graph["region"] = []
        if "starting" in region_data and region_data["starting"]:
            region_graph["__start__"].append(region)
    if not region_graph["__start__"]:
        region_graph["__start__"] = list(region_graph.keys())
    return region_graph


def get_all_paths(region_graph: dict[str, list[str]],
                  start_region: str,
                  destination_region: str,
                  current_path: list[str]) -> list[list[str]]:
    if start_region == destination_region:
        return [[start_region]]
    paths: list[list[str]] = []
    if start_region in region_graph:
        for next_region in region_graph[start_region]:
            if next_region in current_path:
                continue
            updated_path: list[str] = current_path + [next_region]
            possible_paths: list[list[str]] = get_all_paths(region_graph, next_region, destination_region, updated_path)
            for path in possible_paths:
                path.append(start_region)
                paths.append(path)
    return paths


def get_logic_from_paths(paths: list[list[str]], regions: dict[str, any]) -> Logic:
    or_operands: list[Operand] = []
    for path in paths:
        and_operands: list[Operand] = []
        for region in path:
            if region == "__start__":
                continue
            if "requires" in regions[region] and regions[region]["requires"]:
                region_logic: Logic = parse_logic(regions[region]["requires"])
                and_operands.append(Operand(value=region_logic))
        if and_operands:
            and_logic = Logic(op=Operator.AND, operands=and_operands, prim_value="")
            or_operands.append(Operand(value=and_logic))
    or_logic = Logic(op=Operator.OR, operands=or_operands, prim_value="")
    or_logic = convert_to_dnf(or_logic)
    return or_logic


def group_locations_by_key(key: str, locations: list[dict[str, any]]) -> dict[str, list[dict[str, any]]]:
    grouped_locations: dict[str, list[dict[str, any]]] = {}
    for location in locations:
        if key not in location:
            raise SyntaxError(f"Missing grouping key {key} in location {location}")
        if isinstance(location[key], list):
            if location[key]:
                group = location[key][0]
            else:
                group = "default"
        else:
            group = location[key]
        if group in grouped_locations:
            grouped_locations[group].append(location)
        else:
            grouped_locations[group] = [location]
    return grouped_locations


def build_locations_json(locations: list[dict[str, any]],
                         regions: dict[str, any],
                         region_graph: dict[str, list[str]],
                         item_groups: dict[str, list[str]],
                         visibility_options: dict[str, str],
                         total_square_count: int,
                         parent_group: str) -> tuple[int, set[str], list[dict[str, any]]]:
    grouped_by_region: dict[str, list[dict[str, any]]] = group_locations_by_key("region", locations)
    output: list[dict[str, any]] = []
    new_map_names: set[str] = set()
    for region, region_locations in grouped_by_region.items():
        if not region_locations:
            continue
        sections: list[dict[str, any]] = []
        x: int = -1
        y: int = -1
        for location in region_locations:
            section_info: dict[str, any] = {
                "name": location["name"],
                "item_count": 1
            }
            if "requires" in location and location["requires"]:
                location_logic: Logic = parse_logic(location["requires"])
                location_logic = convert_to_dnf(location_logic)
                location_logic = reduce_logic(location_logic, item_groups)
                section_info["access_rules"] = convert_dnf_logic_to_json_object(location_logic)
            if "category" in location and location["category"]:
                visibility_rules: list[str] = []
                for category in location["category"]:
                    if category in visibility_options:
                        for rule in visibility_options[category]:
                            visibility_rules.append(rule)
                if visibility_rules:
                    section_info["visibility_rules"] = visibility_rules
            if "x" in location:
                x = int(location["x"])
            if "y" in location:
                y = int(location["y"])
            sections.append(section_info)
        region_data: dict[str, any] = regions[region]
        map_name: str = "main_map"
        if "map" in region_data:
            map_name = region_data["map"]
        new_map_names.add(map_name)
        map_location: dict[str, any] = {
            "map": map_name,
            "x": x if x >= 0 else (total_square_count % LOCATION_ROW_SIZE) * LOCATION_SPACING,
            "y": y if y >= 0 else (total_square_count // LOCATION_ROW_SIZE) * LOCATION_SPACING
        }
        total_square_count += 1
        region_paths: list[list[str]] = get_all_paths(region_graph, "__start__", region, [])
        region_logic: Logic = get_logic_from_paths(region_paths, regions)
        region_entry: dict[str, any] = {
            "name": region,
            "access_rules": convert_dnf_logic_to_json_object(reduce_logic(region_logic, item_groups)),
            "sections": sections,
            "map_locations": [map_location]
        }
        output.append(region_entry)
    top_level_json: dict[str, any] = {"name": parent_group, "children": output}
    return total_square_count, new_map_names, [top_level_json]


def build_maps_json(map_names: set[str]) -> list[dict[str, any]]:
    output: list[dict[str, any]] = []
    for map_name in sorted(list(map_names)):
        map_dict: dict[str, any] = {
            "name": map_name,
            "img": f"images/maps/{map_name}.png",
            "location_size": 10,
            "location_border_thickness": 1
        }
        output.append(map_dict)
    return output


def build_map_tabs_layout(map_names: set[str]) -> dict[str, any]:
    output: dict[str, any] = {}
    tabs: list[dict[str, any]] = []
    for map_name in sorted(list(map_names)):
        map_layout_dict: dict[str, any] = {
            "type": "map",
            "maps": [map_name]
        }
        tab: dict[str, any] = {
            "title": map_name,
            "content": map_layout_dict
        }
        tabs.append(tab)
    tracker_map_layout: dict[str, any] = {
        "type": "tabbed",
        "tabs": tabs
    }
    output["tracker_map"] = tracker_map_layout
    return output
