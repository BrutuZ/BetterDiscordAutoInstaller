import logging

logger = logging.getLogger("other")


def backslash_path(path: str) -> str:
    """Replaces two slashes (\\) with a backslash (/)"""
    return path.replace("\\", "/")


def remove_item_from_list(item, array: list) -> list:
    return [i for i in array if i != item]
