"""
    Module for randomzing names
"""

from typing import List
import random
import functools


def wrap_name_randomizer(func):
    """
        Wrapper that loads names from file for a certain function.
    """
    with open('forenames.txt', encoding='utf-8') as file:
        names = file.readlines()

    @functools.wraps(func)
    def inner():
        return func(names)

    return inner


@wrap_name_randomizer
def pick_randomized_name(names: List[str]):
    """
        A function that randomly picks a name from the name list.
    """
    return random.choice(names)
