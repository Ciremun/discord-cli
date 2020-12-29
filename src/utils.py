from typing import Iterable

from discord.utils import find


def find_item(name: str, items: Iterable):
    return find(lambda x: x.name.lower() == name, items)
