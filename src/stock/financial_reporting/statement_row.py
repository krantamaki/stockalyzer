"""
Module holding the class implementation for a row in a financial statement

Code using this module needs to be ran from the src directory
"""
from __future__ import annotations
from typing import Callable
import logging
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit


# We use Pythons logging library to control and redirect our outputs.
# To this end be need to define the Logger object
_logger = logging.getLogger(__name__)


from stock.tools import r_squared, order_or_magnitude


class StatementRow():
    """Class wrapper for storing a row of a financial statement. The values will be
    indexed by the reporting dates. Indexing by location in the array is also possible and in such 
    case the order will be from newest to oldest. Additionally, provides useful methods for analysis.

    :param row_name: The name of the row
    :type row_name: str
    :param values: The values for the statement row
    :type values: numpy.ndarray[float]
    :param dates: The reporting dates for the values
    :type dates: numpy.ndarray[numpy.datetime64]

    :raises ValueError: Raised if the lengths of 'values' and 'dates' arrays don't match or improper types given
    """

    def __init__(self, row_name: str, values: np.ndarray[float], dates: np.ndarray[np.datetime64]) -> None:
        """Constructor. See class definition for info on the parameters.
        """
        if len(values) != len(dates):
            _logger.error(f"The lengths of the 'values' and 'dates' arrays must match! ({len(values)} != {len(dates)})")
            raise ValueError(f"The lengths of the 'values' and 'dates' arrays must match! ({len(values)} != {len(dates)})")
        
        try:
            _dates = np.array(dates, dtype='datetime64[D]')
        except ValueError:
            _logger.error(f"The values in the 'dates' array are incompatible with numpy.datetime64 type!")
            raise ValueError(f"The values in the 'dates' array are incompatible with numpy.datetime64 type!")

        _values = np.array(values)
        _value_dict = dict(zip(_dates, _values))

        # Sort the keys so that most recent date is first
        self.__value_dict = dict(sorted(_value_dict.items(), reverse=True))
        self.__name = row_name
        
    def __str__(self) -> str:
        """Method for the string representation of the object.
        """
        if len(self.__value_dict) == 0:
            return f"{self.__name}: "

        value_row = f"{self.__name}:"
        index_row = " " * len(value_row)

        for date, value in self.__value_dict.items():
            width = max(len(str(value)), len(str(date)))
            index_row += " | " + f"{str(date).center(width)}"
            value_row += " | " + f"{str(value).center(width)}"

        return f"{index_row} |\n{value_row} |"
    
    def __getitem__(self, key: np.datetime64) -> float:
        """Method for retrieving a value of the statement row by key (reporting date)

        :param key: The reporting date for which the value is returned
        :type key: numpy.datetime64

        :raises KeyError: Raised if an invalid key passed

        :return: The value associated with given key
        :rtype: float
        """
        valid_key = np.datetime64(key, 'D')
        if valid_key in self.__value_dict.keys():
            return self.__value_dict[valid_key]
        else:
            _logger.error(f"Invalid key {key} passed!")
            raise KeyError(f"Invalid key {key} passed!")
    
    def __setitem__(self, key: np.datetime64, value: float) -> None:
        """Method for setting the value of the statement for a given key (reporting date)

        :param key: The reporting date for which the value is returned
        :type key: numpy.datetime64
        :param value: The new value to be set
        :type value: float

        :return: Void
        :rtype: None
        """
        valid_key = np.datetime64(key, 'D')
        self.__value_dict[valid_key] = value
    
    def iget(self, key: int) -> tuple[np.datetime64, float]:
        """Method for accessing the key-value pair of the reporting date and value reported
        by and integer index. Note that the most recent filing will be at index 0.

        :param key: The integer index used
        :type key: int

        :raises KeyError: Raised if an invalid key passed

        :return: Void
        :rtype: None
        """
        try:
            return list(self.__value_dict.items())[key]
        except IndexError:
            _logger.error(f"Key index {key} out of bounds!")
            raise KeyError(f"Key index {key} out of bounds!")
    
    def name(self) -> str:
        """Method for accessing the name of the row

        :return: The name of the row
        :rtype: str
        """
        return self.__name
    
    def values(self) -> np.ndarray[float]:
        """Method for accessing (a copy of) the stored values

        :return: A copy of the stored values
        :rtype: numpy.ndarray[float]
        """
        return np.array(list(self.__value_dict.values()).copy())
    
    def dates(self) -> np.ndarray[np.datetime64]:
        """Method for accessing (a copy of) the stored keys (dates)

        :return: A copy of the key dates
        :rtype: numpy.ndarray[numpy.datetime64]
        """
        return np.array(list(self.__value_dict.keys()).copy())
    
    def mean(self) -> float:
        """Method for computing the mean of the stored values

        :return: The computed mean
        :rtype: float
        """
        return np.array(list(self.__value_dict.values())).mean()
    
    def std(self) -> float:
        """Method for computing the standard deviation of the stored values

        :return: The computed standard deviation
        :rtype: float
        """
        return np.array(list(self.__value_dict.values())).std()
    
    def predict(self, n_predictions: int = 1, func: str = "linear") -> np.ndarray[float]:
        """Method for making predictions from the existing values. Depending on the chosen
        'func' kwarg value there is three different functions that can be fitted to the values.
        The options are:

            'linear' - fits a linear function of form
                y = bx + a

            'exponential' - fits an exponential function of form
                y = a * \exp{bx}

            'logarithmic' - fits a logarithmic function of form
                y = a * \ln(bx)

        These can be considered to provide different risk attitudes (risk neutral, seeking and 
        averse).

        Of these exponential function has the best interpretation from the 
        mathematical view point. If we assume the values of this row to follow geometric
        Brownian motion

            dX_t = \mu X_t dt + \sigma X_t dB_t

        The future value can be shown to be

            X_t = X_0 \exp{(\mu - \sigma^2 / 2)t + \sigma B_t}

        Which the parameters in the fitted function should imitate.

        :param n_predictions: The number of predictions made. These will be spaced as the existing \
                              values are. Defaults to 1
        :type n_predictions: int, optional
        :param func: The function type to be fitted. Choices are 'linear', 'exponential' and 
                     'logarithmic'. Defaults to 'linear'
        :type func: str, optional

        :raises ValueError: Raised if invalid value passed
        :raises RuntimeError: Raised if fitting was not successful

        :return: The made predictions in an array
        :rtype: np.ndarray[float]
        """
        # The functions to be fitted
        def lin_func(x, a, b):
            return a * x + b
        
        def exp_func(x, a, b):
            return a * np.exp(b * x)
        
        def log_func(x, a, b):
            return a * np.log(b * x)
        
        func_map = {"linear":      lin_func,
                    "exponential": exp_func,
                    "logarithmic": log_func}
        
        try:
            used_func = func_map[func.lower()]
        except KeyError:
            _logger.error(f"Invalid function type {func} passed!")
            raise KeyError(f"Invalid function type {func} passed!")

        y_data = np.flip(np.array(list(self.__value_dict.values())))

        date_data = np.flip(np.array(list(self.__value_dict.keys())).astype(int))
        x_diff = int(np.diff(date_data).mean())
        
        x_data = np.linspace(1, x_diff * len(y_data), len(y_data))

        if func == "exponential":
            # Purely heuristic initial parameters
            init_params = [y_data[0], 10 ** (-order_or_magnitude(y_data[0]))]
        else:
            init_params = [1, 1]

        try:
            popt, _ = curve_fit(used_func, x_data, y_data, p0=init_params)
            _logger.debug(f"Found parameters for {func} function are: {popt} (row '{self.__name}')")
        except RuntimeError:
            _logger.error(f"Could not fit a(n) {func} curve to the values: {y_data}! (row '{self.__name}')")
            raise RuntimeError(f"Could not fit a(n) {func} curve to the values: {y_data}! (row '{self.__name}')")
        
        # Compute the R-squared value for the goodness of fit
        y_fit = used_func(x_data, *popt)

        r2 = r_squared(y_data, y_fit)
        _logger.info(f"R-squared value for {func} function: {r2:.3f} (row '{self.__name}')")

        ret_arr = []
        for i in range(1, n_predictions + 1):
            ret_arr.append(used_func(x_data[-1] + i * x_diff, *popt))
        
        return np.array(ret_arr)
    
    def custom_predict(self, func: Callable, 
                       init_params: tuple[float, ...] = None, n_predictions: int = 1) -> np.ndarray[float]:
        """Method for making predictions from the existing values. This method allows for arbitrary
        function to be fitted. One can consider the chosen function to be equivalent to the utility 
        function from Expected Utility Theorem in Decision Analysis.

        :param func: The function to be fitted. The first parameter should be a float. Other \
                     (arbitrary amount) of parameters are then optimized for.
        :type func: Callable
        :param init_params: The initial guess passed to the optimizer. Defaults to None (ones used)
        :type init_params: tuple[float, ...], optional
        :param n_predictions: The number of predictions made. These will be spaced as the existing \
                              values are. Defaults to 1
        :type n_predictions: int, optional

        :raises RuntimeError : Raised if fitting was not successful

        :return: The made predictions in an array
        :rtype: np.ndarray[float]
        """
        y_data = np.flip(np.array(list(self.__value_dict.values())))

        date_data = np.flip(np.array(list(self.__value_dict.keys())).astype(int))
        x_diff = int(np.diff(date_data).mean())
        
        x_data = np.linspace(1, x_diff * len(y_data), len(y_data))

        try:
            popt, _ = curve_fit(func, x_data, y_data, p0=init_params, )
            _logger.debug(f"Found parameters for the custom function are: {popt}")
        except RuntimeError:
            _logger.error(f"Could not fit a curve to the values: {y_data}!")
            raise RuntimeError(f"Could not fit a curve to the values: {y_data}!")
        
        # Compute the R-squared value for the goodness of fit
        y_fit = func(x_data, *popt)
        
        r2 = r_squared(y_data, y_fit)
        _logger.info(f"R-squared value for custom function: {r2:.3f} (row '{self.__name}')")

        ret_arr = []
        for i in range(1, n_predictions + 1):
            ret_arr.append(func(x_data[-1] + i * x_diff, *popt))
        
        return np.array(ret_arr)


# List the functions and variables accessible in other modules
__all__ = ["StatementRow"]
