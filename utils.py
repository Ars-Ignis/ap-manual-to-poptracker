

def to_snake_case(name: str) -> str:
    snake_str: str = name.lower()
    snake_str = snake_str.replace("'", "")
    snake_str = snake_str.replace("\"", "")
    snake_str = snake_str.replace(" ", "_")
    snake_str = snake_str.replace("\\", "_")
    snake_str = snake_str.replace("/", "_")
    return snake_str


# Copied from Manual's Helpers.py to ensure compatibility
def format_to_valid_identifier(input: str) -> str:
    """Make sure the input is a valid python identifier"""
    input = input.strip()
    if input[:1].isdigit():
        input = "_" + input
    return input.replace(" ", "_")
