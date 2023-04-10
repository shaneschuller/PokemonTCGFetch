import re
from typing import Optional, List

POKEMON_TYPES = {
    "Normal",
    "Fire",
    "Water",
    "Electric",
    "Grass",
    "Ice",
    "Fighting",
    "Poison",
    "Ground",
    "Flying",
    "Psychic",
    "Bug",
    "Rock",
    "Ghost",
    "Dragon",
    "Dark",
    "Steel",
    "Fairy"
}
POKEMON_RARITIES = ["Rare Secret", "Rare Rainbow", "Rare Shiny GX", "Rare Shining", "Rare Shiny", "Rare Holo VMAX",
                    "Amazing Rare", "Rare Holo GX", "Rare Holo LV.X", "Rare Holo EX", "Rare Prime", "Rare ACE",
                    "Rare BREAK", "Rare Prism Star", "Rare Holo Star", "Rare Holo", "LEGEND", "Promo", "Rare Ultra",
                    "Uncommon", "Common"]

OPERATORS = {
    "OR": " or ",
    "NOT": "not ",
    "COMMA": ", "
}


def parse_hp(hp_arg: Optional[str]) -> Optional[str]:
    if hp_arg is None:
        return None
    match = re.match(r"^(\*|\d*)\s*(?:to|TO|To)\s*(\d*|\*)?\s*$", hp_arg.strip())
    if match is None:
        # check if the input is a valid integer
        try:
            int(hp_arg)
            return hp_arg
        except ValueError:
            pass
        raise ValueError(f"Invalid --hp value: {hp_arg}")

    lower_bound = match.group(1)
    upper_bound = match.group(2)

    return f"[{lower_bound} TO {upper_bound}]"


def parse_query(query_arg: Optional[str], items: List[str]) -> List[str]:
    if not query_arg:
        return []

    query_arg = remove_brackets(query_arg)

    query_arg_lower = query_arg.lower()

    if OPERATORS["OR"] in query_arg_lower:
        return handle_or_operator(query_arg_lower, items, parse_query)

    if OPERATORS["NOT"] in query_arg_lower:
        return handle_not_operator(query_arg_lower, items)

    if OPERATORS["COMMA"] in query_arg_lower:
        return handle_comma_operator(query_arg_lower, items, parse_query)

    for item in items:
        if item.lower() == query_arg_lower:
            return [query_arg_lower]

    raise ValueError(f"Invalid value: {query_arg}")


def remove_brackets(s: str) -> str:
    if s.startswith("[") and s.endswith("]"):
        return s[1:-1]
    return s


def handle_or_operator(query_arg_lower: str, items: List[str], parse_fn) -> List[str]:
    subqueries = query_arg_lower.split(OPERATORS["OR"])
    if len(subqueries) < 2 or "" in subqueries:
        raise ValueError("OR operator must have at least two non-empty values")
    queries = set()
    for subquery in subqueries:
        queries.update(parse_fn(subquery, items))
    return list(queries)


def handle_not_operator(query_arg_lower: str, items: List[str]) -> List[str]:
    subquery = query_arg_lower.replace(OPERATORS["NOT"], "")
    if OPERATORS["OR"] in subquery:
        subqueries = subquery.split(OPERATORS["OR"])
        not_items = []
        for item in items:
            if all(sub not in item.lower() for sub in subqueries):
                not_items.append(item.lower())
        return not_items
    else:
        not_items = []
        for item in items:
            if subquery.lower() not in item.lower():
                not_items.append(item.lower())
        return not_items


def handle_comma_operator(query_arg_lower: str, items: List[str], parse_fn) -> List[str]:
    subqueries = query_arg_lower.split(OPERATORS["COMMA"])
    queries = set()
    for subquery in subqueries:
        queries.update(parse_fn(subquery, items))
    return list(queries)


def parse_rarity(rarity_arg: Optional[str]) -> List[str]:
    return parse_query(rarity_arg, POKEMON_RARITIES)


def parse_type(type_arg: Optional[str]) -> List[str]:
    return parse_query(type_arg, list(POKEMON_TYPES))

