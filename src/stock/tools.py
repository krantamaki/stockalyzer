"""
Module for simple helper functions used by the classes
"""
from __future__ import annotations
import numpy as np
import logging


# We use Pythons logging library to control and redirect our outputs.
# To this end be need to define the Logger object
_logger = logging.getLogger(__name__)


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


def symbol_to_params(symbol: str) -> tuple[str, str, np.datetime64, float]:
    """Function that reads from an option symbol the contributing parts i.e.
    the ticker symbol, option type ('call', 'put'), maturity and strike price.
    
    :params symbol: The (standard) option symbol of format <ticker><maturity><type><strike>
    :type symbol: str

    :raises ValueError: Raised if the symbol is of improper format
    
    :return: Tuple containing the ticker symbol, type, maturity and strike
    :rtype: tuple[str, str, np.datetime64, float]
    """
    if len(symbol) <= 15:
        _logger.error(f"Option symbol {symbol} is too short!")
        raise ValueError(f"Option symbol {symbol} is too short!")

    strike = float(f"{symbol[-8:-3]}.{symbol[-3:]}")

    opt_type = ""
    if symbol[-9] == 'C':
        opt_type = "call"
    elif symbol[-9] == 'P':
        opt_type = "put"
    else:
        _logger.error(f"Improper option type {symbol[-9]}!")
        raise ValueError(f"Improper option type {symbol[-9]}!")
        
    maturity = np.datetime64(f"20{symbol[-15:-13]}-{symbol[-13:-11]}-{symbol[-11:-9]}", 'D')
    ticker = symbol[:-15]

    return (ticker, opt_type, maturity, strike)


def r_squared(y_data: np.ndarray[float], y_fit: np.ndarray[float]) -> float:
    """Simple function that computes the coefficient of determination i.e.
    r-squared value

    :param y_data: The original datapoints
    :type y_data: numpy.ndarray[float]
    :param y_data: The fitted datapoints
    :type y_data: numpy.ndarray[float]
    
    :return: The R-squared value
    :rtype: float
    """
    res = np.sum((y_data - y_fit) ** 2)            # Residual sum of squares
    tot = np.sum((y_data - np.mean(y_data)) ** 2)  # total sum of squares

    r2 = 1 - (res / tot)

    return r2


__all__ = ["map_to_None", "strdate", "symbol_to_params", "r_squared"]
