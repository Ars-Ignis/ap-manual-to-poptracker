from logic import *


LOCATION_ROW_SIZE = 20
LOCATION_SPACING = 25


def build_region_graph(regions: dict[str, any]) -> dict[str, list[str]]:
    region_graph: dict[str, list[str]] = {}
    for region, region_data in regions.items():
        region_graph[region] = region_data["connects_to"]
        if "starting" in region_data and region_data["starting"]:
            region_graph["__start__"] = [region]
    return region_graph


def get_all_paths(region_graph: dict[str, list[str]],
                  start_region: str,
                  destination_region: str,
                  current_path: list[str]) -> list[list[str]]:
    if start_region == destination_region:
        return [[start_region]]
    paths: list[list[str]] = []
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
            group = location[key][0]
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
                         parent_group: str) -> tuple[int, list[dict[str, any]]]:
    grouped_by_region: dict[str, list[dict[str, any]]] = group_locations_by_key("region", locations)
    output: list[dict[str, any]] = []
    for region, region_locations in grouped_by_region.items():
        if not region_locations:
            continue
        children: list[dict[str, any]] = []
        for location in region_locations:
            section_info: dict[str, any] = {
                "name": location["name"],
                "item_count": 1
            }
            map_location: dict[str, any] = {
                "map": "main_map",
                "x": (total_square_count % LOCATION_ROW_SIZE) * LOCATION_SPACING,
                "y": (total_square_count // LOCATION_ROW_SIZE) * LOCATION_SPACING
            }
            child_info: dict[str, any] = {
                "name": location["name"],
                "sections": [section_info],
                "map_locations": [map_location]
            }
            total_square_count += 1
            if "requires" in location and location["requires"]:
                location_logic: Logic = parse_logic(location["requires"])
                location_logic = convert_to_dnf(location_logic)
                location_logic = reduce_logic(location_logic, item_groups)
                child_info["access_rules"] = convert_dnf_logic_to_json_object(location_logic)
            if "category" in location:
                visibility_rules: list[str] = []
                for category, rule in visibility_options.items():
                    if category in location["category"]:
                        visibility_rules.append(rule)
                child_info["visibility_rules"] = visibility_rules
            children.append(child_info)
        region_paths: list[list[str]] = get_all_paths(region_graph, "__start__", region, [])
        region_logic: Logic = get_logic_from_paths(region_paths, regions)
        region_entry: dict[str, any] = {
            "name": region,
            "access_rules": convert_dnf_logic_to_json_object(reduce_logic(region_logic, item_groups)),
            "children": children
        }
        output.append(region_entry)
    top_level_json: dict[str, any] = {"name": parent_group, "children": output}
    return total_square_count, [top_level_json]
