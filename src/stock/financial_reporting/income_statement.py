"""
Module holding the class implementation for an income statement of a company

Note for this code to function correctly, the code using it must be ran from
the src directory.
"""
from __future__ import annotations
from typing import Union
import pandas as pd
import numpy as np
import logging
from pathlib import Path


# We use Pythons logging library to control and redirect our outputs.
# To this end be need to define the Logger object
_logger = logging.getLogger(__name__)


# After we have defined the logger we can import other modules
import config
import db
from stock.tools import *
from stock.schema import *
from stock.financial_reporting import StatementRow


# Default values used in case the config values not accessible
save_at_exit = False  # Should the income statement be saved to memory when exiting the program


class IncomeStmt():
    """Class wrapper for storing the income statement for a given company. There are
    two ways of initializing an IncomeStmt object. One way is by passing the income statement
    information as a Pandas dataframe to kwarg 'df' or initializing with only the ticker and using 'read_df' method.
    Alternatively, one can initialize the object with kwarg 'load' set to True, which loads the information from 
    the default database. If dataframe is given while 'load' is set to True, the dataframe will take precedence 
    and 'load' ignored. Finally, one can initialize the object with only the 'ticker' defined and loading afterwards 
    with 'load' method. The keys to access rows of the financial statement will be the same as with Yahoo Finance API
    (see in schema.py 'incomeStmt_map' the 'name' value). This can also be accessed with the 'keys' method.

    :param ticker: The ticker symbol of the company, which statement we are initializing.
    :type ticker: str
    :param currency: The currency in which the values are given
    :type currency: str
    :param df: Dataframe containing as columns the fields of the income statement. Columns should \
               use the same naming convention as the database (see schema.py for more information). If \
               such is not the case the 'altkeys' kwarg should be set to have a mapping from the database \
               column names to the keys in the dataframe. Defaults to None.
    :type df: pandas.DataFrame, optional
    :param altkeys: The alternative keys used to access info from the dataframe. Defaults to None
    :type altkeys: dict[str, str]
    :param load: Boolean flag telling if the income statement should be loaded from (default) database. \
                 If both 'df' and 'load' are defined df will take precedence. Defaults to False.
    :type load: bool, optional
    """

    def __init__(self, ticker: str, currency: str, df: pd.DataFrame = None, altkeys: dict[str, str] = None, load: bool = False) -> None:
        """Constructor. See class definition for info on the parameters.
        """
        # Boolean to quickly check that object is properly initialized
        self.__proper_init = False

        # Define the statement rows. These are the columns starting with 'totRevenue' in the db schema
        statement_start = list(incomeStmt_map.keys()).index('totRevenue')
        self.__row_map = map_to_None(list(incomeStmt_map.keys())[statement_start:])

        # The names of the rows should be the same as with Yahoo Finance API
        # These can be retrieved from schema.py
        db_keys = list(incomeStmt_map.keys())
        financial_keys = [incomeStmt_map[key]["name"] for key in db_keys]
        self.__row_name_map = dict(zip(financial_keys, db_keys)[statement_start:])

        # Other information
        self.__ticker = ticker
        self.__currency = currency
        self.__lastUpdate = None
        self.__dateIndex = None

        self.__altkeys = None

        # Process the other inputs
        if df is not None:
            self.read_df(df, altkeys=altkeys)

        if load and df is None:
            self.load()

    def __del__(self) -> None:
        """The destructor. Called when the object is garbage collected. 
        """
        if config.config_done():
            if config.get_value("Database", "SaveAtExit").lower() == "yes":
                self.save()
        elif save_at_exit:
            self.save()

    def __str__(self) -> str:
        """Method for the string representation of the object.
        TODO: Check the order of magnitude of values and give some numbers in thousands, millions etc.
        """
        ret_str = f"INCOME STATEMENT\n  \
                    Ticker: {self.__ticker}; Last Updated: {self.__lastUpdate}; Currency: {self.__currency}"

        if not self.__proper_init:
            return f"{ret_str}<uninitialized>"
        
        max_name_width = max([len(name) for name in self.__row_name_map])
        max_column_widths = [max([len(str(row[date])) for row in self.__row_map.values()] + [str(date)]) for date in self.__dateIndex]

        index_str = " " * (max_name_width + 1) + " | " +  " | ".join([str(date).center(max_column_widths[i]) for i, date in enumerate(self.__dateIndex)]) + " |"

        total_width = len(index_str)
        ret_str += '=' * total_width + "\n"
        ret_str += index_str + "\n"

        for row_name in self.__row_name_map:
            row = self.__row_map[row_name]
            row_str = row_name + " | " +  " | ".join([str(row[date]).center(max_column_widths[i]) for i, date in enumerate(self.__dateIndex)]) + " |"
            ret_str += row_str + "\n"

        ret_str += '=' * total_width + "\n"

        return ret_str

    def __getitem__(self, key: str) -> StatementRow:
        """Method for accessing the values of some row in the statement.

        :param key: The key of which value will be returned (same naming convention is used as in Yahoo Finance)
        :type key: str

        :raises KeyError: Raised if key not found
        :raises RuntimeError: Raised if statement object is not properly initialized

        :return: A StatementRow object corresponding with the given row key
        :rtype: StatementRow
        """
        if not self.__proper_init:
            _logger.error(f"Statement object must be properly initialized!")
            raise RuntimeError(f"Statement object must be properly initialized!")

        try:
            return self.__row_map[self.__row_name_map[key]]
        except KeyError:
            _logger.error(f"Improper row name {key} passed!")
            raise KeyError(f"Improper row name {key} passed!")

    def __setitem__(self, key: str, value: Union[StatementRow, list[float]]) -> None:
        """Method for setting the values for some row in the statement. The given values can be passed as either
        a StatementRow object or as a list of floating point values. In the case that the dates in the passed StatementRow
        object don't match the one for the rest of the statement an error will be raised. This also dictates that in the 
        StatementRow object as well as in the list needs to be as many values as are on other rows. 

        Note that creation of new keys is not permitted.

        :param key: The name of the row (same naming convention is used as in Yahoo Finance)
        :type key: str
        :param value: The values as either a StatementRow object or a list of floating point values.
        :type value: Union[StatementRow, list[float]]

        :raises KeyError: Raised if key not found
        :raises ValueError: Raised if invalid values passed
        :raises RuntimeError: Raised if statement object is not properly initialized

        :return: Void
        :rtype: None
        """
        if not self.__proper_init:
            _logger.error(f"Statement object must be properly initialized!")
            raise RuntimeError(f"Statement object must be properly initialized!")
        
        if key not in self.__row_name_map:
            _logger.error(f"Improper row name {key} passed!")
            raise KeyError(f"Improper row name {key} passed!")
        
        if isinstance(value, StatementRow):
            if self.__dateIndex != value.dates():
                _logger.error(f"The given statement row has incompatible date index! ({value.dates()} != {self.__dateIndex})")
                raise ValueError(f"The given statement row has incompatible date index! ({StatementRow.dates()})")
            else:
                self.__row_map[self.__row_name_map[key]] = value
        else:
            if len(self.__dateIndex != len(value)):
                _logger.error(f"The number of values passed doesn't match the length of the date index! ({len(value)} != {len(self.__dateIndex)})")
                raise ValueError(f"The number of values passed doesn't match the length of the date index! ({len(value)} != {len(self.__dateIndex)})")
            else:
                self.__row_map[self.__row_name_map[key]] = StatementRow(key, value, self.__dateIndex)

    def keys(self) -> list[str]:
        """Method for accessing the keys (row names) in the object.

        :return: The keys as a list
        :rtype: list[str]
        """
        return list(self.__row_name_map.keys())

    def read_df(self, df: pd.DataFrame, altkeys: dict[str, str] = None) -> None:
        """Method for reading the required statement values from a DataFrame. The dataframe should
        have the database columns ('totRevenue' onwards see schema.py) as column keys and the reporting
        dates as index. This is the format in which the API is stockAPI module should give the statement
        with the 'income_statement' method.

        If 'altkeys' kwarg was passed when initialized, will check with both them and the database columns.
        
        Resets the whole object, so some loss of information is possible.

        :param df: The DataFrame to be read
        :type df: pandas.DataFrame
        :param altkeys: A mapping from the database columns to some alternative keys used as the columns of \
                        the DataFrame. Defaults to None
        :type altkeys: dict[str, str], optional

        :raises ValueError: Raised if the given DataFrame has invalid columns or dates, or the altkeys are invalid

        :return: Void
        :rtype: None
        """
        if altkeys is not None:
            db_keys = list(incomeStmt_map.keys())
            statement_start = db_keys.index['totRevenue']
            if set(db_keys[statement_start:]).issubset(set(altkeys.keys())):
                self.__altkeys = altkeys
            else:
                _logger.error(f"Alternative keys must contain all of the column names!")
                raise ValueError(f"Alternative keys must contain all of the column names!")

        df_keys = df.columns
        chosen_keys = None

        if set(df_keys).issubset(set(self.__row_map.keys())):
            chosen_keys = list(self.__row_map.keys())

        if self.__altkeys is not None and chosen_keys is None:
            if set(df_keys).issubset(set(self.__altkeys.values())):
                chosen_keys = list(self.__altkeys.values)

        if chosen_keys is None:
            _logger.error(f"Given DataFrame contains invalid columns!")
            raise ValueError(f"Given DataFrame contains invalid columns!")
        
        # Reset the object
        statement_start = list(incomeStmt_map.keys()).index('totRevenue')
        self.__row_map = map_to_None(chosen_keys)
        self.__lastUpdate = np.datetime64('today', 'D')

        dates = np.array(df.index.values, dtype="datetime64[D]")
        self.__dateIndex = dates

        # Read the values
        for key in df_keys:
            values = df[key].values
            row = StatementRow(key, values, dates)
            self.__row_map[key] = row

    def load(self) -> None:
        """Method for loading the statement info from the database. Assumes the connection is
        already made and that the database follows the schema outlined in schema.py.

        :raises RuntimeError: Raised if statement for the given ticker cannot be retrieved

        :return: Void
        :rtype: None
        """
        try:
            tups = db.get_by_value(self.__ticker, "incomeStmt", "ticker")
        except ValueError:
            _logger.error(f"No income statement for {self.__ticker} stored in the database!")
            raise RuntimeError(f"No income statement for {self.__ticker} stored in the database!")
        
        db_keys = list(incomeStmt_map.keys())
        statement_start = db_keys.index('totRevenue')

        row_dict = dict(zip(db_keys, tups[0]))

        dates = np.array(row_dict['dateIndex'].split(':'), dtype="datetime64[D]")
        last_update = np.datetime64(row_dict['lastUpdate'], 'D')

        self.__lastUpdate = last_update
        self.__dateIndex = dates

        for row_name, value_str in list(row_dict.items())[statement_start:]:
            values = map_to_float(value_str.split(':'))
            row = StatementRow(row_name, values, dates)
            self.__row_map[row_name] = row

    def save(self) -> None:
        """Method for saving the statement info in a database. Assumes the connection is
        already made and that the database follows the schema outlined in schema.py.

        :raises RuntimeError: Raised if saving fails

        :return: Void
        :rtype: None
        """
        db_keys = list(incomeStmt_map.keys())

        # Place the non-statement specific values in a list
        row_values = [self.__ticker, str(self.__lastUpdate), ':'.join([str(date) for date in self.__dateIndex])]

        # Go over the table columns and add the values to the list
        for key in db_keys:
            if self.__altkeys is not None:
                values = self.__row_map[self.__altkeys[key]]
            else:
                values = self.__row_map[key]

            if values is not None:
                row_values.append(':'.join(values))
            else:
                row_values.append(':'.join([None] * len(self.__dateIndex)))
        
        db_row_exists = len(db.get_by_value(self.__ticker, "incomeStmt", "ticker")) > 0

        if db_row_exists:
            db.update_by_value(self.__ticker, zip(db_keys, row_values), "incomeStmt", "ticker")
        else:
            db.insert_row(row_values, "incomeStmt")


__all__ = ["IncomeStmt"]
