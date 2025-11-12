from utils import to_snake_case


def get_item_groups(items: list[dict[str, any]]) -> dict[str, list[str]]:
    item_groups: dict[str, list[str]] = {}
    for item in items:
        if (("progression" not in item or not item["progression"]) and
           ("progression_skip_balancing" not in item or not item["progression_skip_balancing"])):
            continue
        if "category" in item:
            for category in item["category"]:
                if category in item_groups:
                    item_groups[category].append(item["name"])
                else:
                    item_groups[category] = [item["name"]]
    return item_groups


def parse_items(items: dict[str, any]) -> tuple[list[dict[str, any]], dict[str, dict[str, int]]]:
    # Create output object for items
    poptracker_items: list[dict[str, any]] = []
    item_values: dict[str, dict[str, int]] = {}
    for item in items:
        if (("progression" not in item or not item["progression"]) and
           ("progression_skip_balancing" not in item or not item["progression_skip_balancing"])):
            continue
        poptracker_item: dict[str, any] = {}
        count: int = int(item["count"]) if "count" in item else 1
        has_multiple: bool = count > 1
        poptracker_item["name"] = item["name"]
        poptracker_item["type"] = "consumable" if has_multiple else "toggle"
        poptracker_item["loop"] = "true"
        poptracker_item["img"] = f"images/items/{to_snake_case(item['name'])}.png"
        poptracker_item["codes"] = to_snake_case(item["name"])
        if has_multiple:
            poptracker_item["min_quantity"] = 0
            poptracker_item["max_quantity"] = count
        poptracker_items.append(poptracker_item)
        if "value" in item and item["value"]:
            for value_category, value_amount in item["value"].items():
                if value_category in item_values:
                    item_values[value_category][item["name"]] = int(value_amount)
                else:
                    item_values[value_category] = {item["name"] : int(value_amount)}

    return poptracker_items, item_values


def build_item_layout(item_groups: dict[str, list[str]], row_size: int) -> list[dict[str, any]]:
    layout_groups: dict[str, any] = {}
    content: list[dict[str, any]] = []
    seen_items: set[str] = set()
    for category, items in item_groups.items():
        filtered_items: list[str] = [item for item in items if item not in seen_items]
        if not filtered_items:
            continue
        rows: list[list[str]] = []
        for i in range((len(filtered_items)//row_size)+1):
            row: list[str] = []
            for item in filtered_items[i*row_size:(i+1)*row_size]:
                row.append(to_snake_case(item))
                seen_items.add(item)
            while len(row) < row_size:
                row.append("")
            rows.append(row)
        group_layout: dict[str, any] = {"type": "itemgrid", "h_alignment": "center", "item_size": 40,
                                        "item_margin": "4,4", "rows": rows}
        layout_groups[to_snake_case(category)] = group_layout
        content_entry: dict[str, any] = {"type": "layout", "dropshadow": False, "margin": 0,
                                         "key": to_snake_case(category)}
        content.append(content_entry)

    tracker_items: dict[str, any] = {"type": "array", "orientation": "vertical", "style": "wrap", "content": content}
    layout_groups["tracker_items"] = tracker_items
    return layout_groups


