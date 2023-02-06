"""
    Module for randomzing names
"""

from typing import List
import random
import functools


class NameRandomizer:
    """
        A class to randomly pick names.
    """
    names: List[str]

    def __init__(self) -> None:
        """
            Class initializer will fill name list from a file.
        """
        with open('forenames.txt', encoding='utf-8') as file:
            self.names = file.readlines()

    def pick(self):
        """
            A function that randomly picks a name from the name list.
        """
        return random.choice(self.names)

def wrap_name_randomizer(func):
    """
        Wrapper that creates name randomizer object for a certain function.
    """
    nrand = NameRandomizer()

    @functools.wraps(func)
    def inner():
        return pick_randomized_name(nrand)

    return inner

@wrap_name_randomizer
def pick_randomized_name(nrand: NameRandomizer):
    """
        Picks a random name via a name picker class.
    """
    return nrand.pick()
