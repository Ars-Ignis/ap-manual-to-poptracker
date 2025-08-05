

def to_snake_case(name: str) -> str:
    snake_str: str = name.lower()
    snake_str = snake_str.replace("'", "")
    snake_str = snake_str.replace("\"", "")
    snake_str = snake_str.replace(" ", "_")
    snake_str = snake_str.replace("\\", "_")
    snake_str = snake_str.replace("/", "_")
    return snake_str
