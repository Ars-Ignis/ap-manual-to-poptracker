from typing import NamedTuple
from enum import Enum
from utils import *


BUILT_IN_FUNCTIONS = [
    "ItemValue",
    "OptOne",
    "OptAll",
    "YamlEnabled",
    "YamlDisabled",
    "YamlCompare",
]


class Operator(Enum):
    AND = 0
    OR = 1
    PRIMITIVE = 2


class Operand(NamedTuple):
    value: "Logic"


class Logic(NamedTuple):
    op: Operator
    operands: list[Operand]
    prim_value: str


def convert_tokens_to_logic(tokens: list[str]) -> Logic:
    if len(tokens) == 1:
        # this is either a string that needs to be tokenized and parsed, or a primitive
        token: str = tokens[0]
        if token.startswith("|") and token.endswith("|") and token.count("|") == 2:
            # this is a primitive
            return Logic(op=Operator.PRIMITIVE, operands=[], prim_value=token[1:-1])
        elif token.startswith("{") and token.endswith("}") and token.count("{") == 1:
            # this is a function, write as a primitive in PopTracker function syntax
            function_name: str = token[1:token.find("(")]
            function_params: str = token[token.find("(")+1:token.find(")")]
            function_string: str = f"${function_name}"
            if function_params:
                modified_param_string: str = ""
                if function_name == "ItemValue":
                    # delimiter is a colon
                    value_category, _, target_value = function_params.partition(":")
                    modified_param_string = "|" + value_category.rstrip() + "|" + target_value.lstrip()
                elif function_name == "YamlCompare":
                    # delimiter is whitespace
                    param_list: list[str] = function_params.split()
                    if len(param_list) != 3:
                        raise SyntaxError(f"YamlCompare takes exactly three parameters, separated by whitespace! "
                                          f"Parameters found: {function_params}")
                    modified_param_string = "|" + "|".join(param_list)
                else:
                    # delimiter is a comma
                    param_list: list[str] = function_params.split(",")
                    for param in param_list:
                        modified_param_string += "|" + param.lstrip().rstrip()
                function_string += modified_param_string
            return Logic(op=Operator.PRIMITIVE, operands=[], prim_value=function_string)
        else:
            # this is a string that needs to be further broken down
            return parse_logic(token)

    # check to see if top-level operators all match
    if "or" in tokens:
        # top-level operator should be an or, so group the ands together
        return_logic: Logic = Logic(op=Operator.OR, operands=[], prim_value="")
        while "or" in tokens:
            or_index = tokens.index("or")
            subtokens = tokens[0:or_index]
            subtoken_logic: Logic = convert_tokens_to_logic(subtokens)
            return_logic.operands.append(Operand(value=subtoken_logic))
            tokens = tokens[or_index+1:]
        subtoken_logic: Logic = convert_tokens_to_logic(tokens)
        return_logic.operands.append(Operand(value=subtoken_logic))
        return return_logic
    elif "and" in tokens:
        # there are no ors, so everything should be and-ed
        return_logic: Logic = Logic(op=Operator.AND, operands=[], prim_value="")
        while "and" in tokens:
            and_index = tokens.index("and")
            subtokens = tokens[0:and_index]
            subtoken_logic: Logic = convert_tokens_to_logic(subtokens)
            return_logic.operands.append(Operand(value=subtoken_logic))
            tokens = tokens[and_index+1:]
        subtoken_logic: Logic = convert_tokens_to_logic(tokens)
        return_logic.operands.append(Operand(value=subtoken_logic))
        return return_logic
    else:
        # multiple tokens, but no operators; raise an exception
        raise SyntaxError(f"Found two operands with no operator {tokens}")


def parse_logic(logic: str) -> Logic:
    index: int = 0
    tokens: list[str] = []
    # tokenize the logic
    while index < len(logic):
        current_char: str = logic[index:index+1]
        if current_char == '(':
            # parentheses: find the matching close paren
            cur_depth: int = 1
            inner_index = index + 1
            while cur_depth >= 1 and inner_index <= len(logic):
                inner_char: str = logic[inner_index:inner_index+1]
                if inner_char == '(':
                    cur_depth += 1
                elif inner_char == ')':
                    cur_depth -= 1
                inner_index += 1
            if cur_depth != 0:
                raise SyntaxError(f"Mismatched parenthesis starting at index {index} for rule {logic}")
            tokens.append(logic[index+1:inner_index-1])
            index = inner_index + 1
        elif current_char == '|':
            end_index = logic.find("|", index+1)
            if end_index == -1:
                raise SyntaxError(f"Mismatched pipes starting at index {index} for rule {logic}")
            tokens.append(logic[index:end_index+1])
            index = end_index + 1
        elif current_char == '{':
            end_index = logic.find("}", index+1)
            if end_index == -1:
                raise SyntaxError(f"Mismatched braces starting at index {index} for rule {logic}")
            tokens.append(logic[index:end_index+1])
            index = end_index + 1
        elif current_char.isspace():
            index += 1
            continue
        else:
            # should be an operator
            if logic[index:index+3].lower() == "and":
                index += 3
                tokens.append("and")
            elif logic[index:index+2].lower() == "or":
                index += 2
                tokens.append("or")
            else:
                raise SyntaxError(f"Unrecognized logic syntax at index {index} of rule {logic}")

    return convert_tokens_to_logic(tokens)


def is_dnf(logic: Logic) -> bool:
    # strict DNF only
    if logic.op != Operator.OR:
        return False
    for operand in logic.operands:
        if operand.value.op != Operator.AND:
            return False
        for primitive in operand.value.operands:
            if primitive.value.op != Operator.PRIMITIVE:
                return False
    return True


def convert_to_dnf(logic: Logic) -> Logic:
    if is_dnf(logic):
        return logic
    if logic.op == Operator.PRIMITIVE:
        # force into strict DNF form
        primitive_operand: Operand = Operand(value=logic)
        and_logic: Logic = Logic(op=Operator.AND, operands=[primitive_operand], prim_value="")
        and_operand: Operand = Operand(value=and_logic)
        return Logic(op=Operator.OR, operands=[and_operand], prim_value="")
    if logic.op == Operator.AND:
        or_children: list[Operand] = [operand for operand in logic.operands if operand.value.op == Operator.OR]
        and_children: list[Operand] = [operand for operand in logic.operands if operand.value.op == Operator.AND]
        prim_children: list[Operand] = [operand for operand in logic.operands if operand.value.op == Operator.PRIMITIVE]
        if and_children:
            new_children: list[Operand] = or_children + prim_children
            for child in and_children:
                new_children.extend(child.value.operands)
            return convert_to_dnf(Logic(op=Operator.AND, operands=new_children, prim_value=""))
        elif or_children:
            # this is where we do the hard work
            # all children at this point are ors or primitives, and there is at least one or
            child_to_distribute: Operand = or_children.pop()
            new_top_level_children: list[Operand] = []
            for distributee in child_to_distribute.value.operands:
                new_mid_level_children: list[Operand] = or_children + prim_children
                new_mid_level_children.append(distributee)
                new_mid_level_logic: Logic = Logic(op=Operator.AND, operands=new_mid_level_children, prim_value="")
                new_top_level_children.append(Operand(value=new_mid_level_logic))
            new_top_level_logic: Logic = Logic(op=Operator.OR, operands=new_top_level_children, prim_value="")
            return convert_to_dnf(new_top_level_logic)
        else:
            # this is just primitives, so make a top-level OR with just this as a child
            and_operand: Operand = Operand(value=logic)
            return Logic(op=Operator.OR, operands=[and_operand], prim_value="")
    else:
        # or operator, but not in the right final format; convert all the children, then merge
        new_operands: list[Operand] = []
        for operand in logic.operands:
            converted_child: Logic = convert_to_dnf(operand.value)
            new_operands.extend(converted_child.operands)
        return Logic(op=Operator.OR, operands=new_operands, prim_value="")


def print_logic(logic: Logic) -> str:
    if not is_dnf(logic):
        raise AssertionError(f"print_logic works with logic in DNF form only! {logic}")
    return_str: str = "[\n\""
    first_and: bool = True
    for and_child in logic.operands:
        if first_and:
            first_and = False
        else:
            return_str += ",\n\""
        first_prim: bool = True
        for prim_child in and_child.value.operands:
            if first_prim:
                first_prim = False
            else:
                return_str += ", "
            return_str += prim_child.value.prim_value
        return_str += "\""
    return_str += "\n],"
    return return_str


def reduce_logic(logic: Logic, item_groups: dict[str, list[str]]) -> Logic:
    if not is_dnf(logic):
        raise AssertionError(f"reduce_logic works with logic in DNF form only! {logic}")
    # first reduce all the children
    all_primitive_sets: list(set(str)) = []
    for or_operand in logic.operands:
        primitive_set: set(str) = set()
        item_group_counts: dict[str, int] = {}
        for and_operand in or_operand.value.operands:
            value: str = and_operand.value.prim_value
            if value.startswith("@"):
                item_group: str = value[1:value.index(":")]
                count: int = value[value.index(":")+1:len(value)]
                if item_group in item_group_counts:
                    if count > item_group_counts[item_group]:
                        item_group_counts[item_group] = count
                else:
                    item_group_counts[item_group] = count
            else:
                primitive_set.add(value)
        for item_group, count in item_group_counts.items():
            primitive_set.add(f"@{item_group}:{str(count)}")
        all_primitive_sets.append(primitive_set)

    # second, check for subsets
    def sort_key(s: set) -> int:
        return len(s)
    all_primitive_sets.sort(key=sort_key)
    relevant_primitive_sets: list(set(str)) = []
    for primitive_set in all_primitive_sets:
        potential_item_group_counts: dict[str, int] = {}
        potential_comparison_set: set(str) = set()
        for potential_primitive in list(sorted(primitive_set)):
            if potential_primitive.startswith("@"):
                item_group: str = potential_primitive[1:potential_primitive.index(":")]
                count: int = int(potential_primitive[potential_primitive.index(":")+1:len(potential_primitive)])
                potential_item_group_counts[item_group] = count
            else:
                potential_comparison_set.add(potential_primitive)
        for relevant_primitive_set in relevant_primitive_sets:
            relevant_item_group_counts: dict[str, int] = {}
            relevant_comparison_set: set(str) = set()
            for relevant_primitive in list(sorted(relevant_primitive_set)):
                if relevant_primitive.startswith("@"):
                    item_group: str = relevant_primitive[1:relevant_primitive.index(":")]
                    count: int = int(relevant_primitive[relevant_primitive.index(":")+1:len(relevant_primitive)])
                    relevant_item_group_counts[item_group] = count
                else:
                    relevant_comparison_set.add(relevant_primitive)
            if not (potential_comparison_set >= relevant_comparison_set):
                continue
            for item_group, relevant_count in relevant_item_group_counts.items():
                if item_group in potential_item_group_counts and potential_item_group_counts[item_group] >= relevant_count:
                    continue
                else:
                    item_group_list: list[str] = item_groups[item_group]
                    found_count: int = 0
                    for potential_item in list(sorted(potential_comparison_set)):
                        if potential_item in item_group_list:
                            found_count += 1
                            if found_count >= relevant_count:
                                # we found enough, move on to the next group
                                break
                    else:
                        # we didn't find enough, give up
                        break
            else:
                # we found enough of everything, so this set is not relevant
                break
        else:
            relevant_primitive_sets.append(primitive_set)

    # third, build back up into Logic
    new_or_operands: list[Operand] = []
    for primitive_set in relevant_primitive_sets:
        new_and_operands: list[Operand] = []
        for primitive in sorted(list(primitive_set)):
            new_and_operands.append(Operand(value=Logic(op=Operator.PRIMITIVE, operands=[], prim_value=primitive)))
        new_and_logic: Logic = Logic(op=Operator.AND, operands=new_and_operands, prim_value="")
        new_or_operands.append(Operand(value=new_and_logic))
    new_or_logic: Logic = Logic(op=Operator.OR, operands=new_or_operands, prim_value="")
    return new_or_logic


def convert_dnf_logic_to_json_object(logic: Logic) -> tuple[list[str], dict[str, int]]:
    if not is_dnf(logic):
        raise AssertionError(f"convert_dnf_logic_to_json_object works with logic in DNF form only! {logic}")
    json_object: list[str] = []
    functions: dict[str, int] = {}
    for or_operand in logic.operands:
        operand_string: str = ""
        first_operand: bool = True
        for and_operand in or_operand.value.operands:
            if first_operand:
                first_operand = False
            else:
                operand_string += ", "
            prim_value: str = and_operand.value.prim_value
            if prim_value.startswith("@"):
                item_group: str = prim_value[1:prim_value.index(":")]
                count: int = int(prim_value[prim_value.index(":")+1:len(prim_value)])
                operand_string += f"$has_count_from_group|{item_group}|{count}"
            elif prim_value.startswith("$"):
                function_name: str = prim_value[1:]
                pipe_index: int = prim_value.find("|")
                if pipe_index >= 0:
                    function_name: str = prim_value[1:pipe_index]
                if function_name not in BUILT_IN_FUNCTIONS and function_name not in functions:
                    functions[function_name] = prim_value.count("|")
                operand_string += prim_value
            else:
                operand_string += to_snake_case(prim_value)
        json_object.append(operand_string)
    return json_object, functions
