"""
Module for simple helper functions used by the classes
"""
from __future__ import annotations
import numpy as np


def map_to_None(keys: list[str]) -> dict[str, None]:
    """Function that takes a list of keys and returns a dictionary
    with said keys that map to None values.

    :param keys: The list of keys
    :type keys: list[str]

    :return: A dictionary where the given keys map to None values
    :rtype: dict[str, None]
    """
    return dict([(key, None) for key in keys])


def strdate(date: np.datetime64) -> str:
    """Function that converts a numpy datetime64 object or
    string into a valid date format 'yyyy-mm-dd'

    :param date: The date of interest
    :type date: np.datetime64

    :return: The date in valid format
    :rtype: str
    """
    return str(np.datetime64(date, 'D'))[:10]


__all__ = ["map_to_None", "strdate"]
