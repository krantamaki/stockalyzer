"""
Class wrapper around the yfinance library to conform with the abcAPI abstact base class

Note for this code to function correctly, the code using it must be ran from
the src directory.
"""
from __future__ import annotations
import logging
import yfinance as yf
import pandas as pd
import numpy as np
import requests


# We use Pythons logging library to control and redirect our outputs.
# To this end be need to define the Logger object
_logger = logging.getLogger(__name__)


# After we have defined the logger we can import other modules
from stock.schema import *
from stock.tools import *
from stock.stockAPI.api_abc import abcAPI


class YahooAPI(abcAPI):
    """Wrapper class around the yfinance Ticker class to conform with the abcAPI abstract base class.
    When initialized retrieves the corresponding yfinance.Ticker object for the given ticker symbol
    and checks that it is valid i.e. it exists and is a stock.

    :param ticker: The ticker symbol for the stock of interest
    :type ticker: str

    :raises ValueError: Raised if invalid ticker symbol passed.
    """
  
    def __init__(self, ticker: str) -> None:
        """Constructor. See class definition for info on the parameters.
        """
        self.__ticker = ticker
        self.__yfTicker = yf.Ticker(ticker)
        
        try:
            self.__info = self.__yfTicker.info
            self.__info["quoteType"]
        except KeyError:
            _logger.error(f"Invalid ticker symbol {ticker} given!")
            raise ValueError(f"Invalid ticker symbol {ticker} given!")
        except requests.exceptions.HTTPError as e:
            _logger.error(f"Could not connect to Yahoo Finance API: {e}! Consider updating yfinance library.")
            raise ValueError(f"Could not connect to Yahoo Finance API: {e}! Consider updating yfinance library.")
        
        if self.__info["quoteType"] != "EQUITY":
            _logger.error(f"Given ticker {ticker} is of impoper type {self.__info['quoteType']}!")
            raise ValueError(f"Given ticker {ticker} is of impoper type {self.__info['quoteType']}!")

    def description(self) -> str:
        """Method for accessing a description of the company.
        
        :return: The description
        :rtype: str
        """
        return self.__info["longBusinessSummary"]
    
    def summary(self, altkeys: dict[str, str] = None) -> dict[str, any]:
        """Method for accessing basic information for the stock. The basic information
        is defined as the column values for the stock table (see README or schema.py). If
        some of the information cannot be reached the value will default to None. The keys in
        the returned dictionary will be the column names for the stock table unless alternative
        keys are passed as a kwarg.

        :param altkeys: Alternative keys as a dictionary of form column name -> alternative key \
                        Defaults to None.
        :type altkeys: dict[str, str], optional

        :raises ValueError: Raised if the alternative keys don't contain all of the column names as keys.

        :return: Dictionary mapping the column names or alternative keys to associated values
        :rtype: dict[str, any]
        """
        info_keys = [None, None, "exchange", "currentPrice", "currency", None, None, "marketCap",
                     "trailingEps", "trailingPE", "debtToEquity", "dividendRate", "dividendYield", "beta"]
        db_keys = list(stock_map.keys())

        if altkeys is not None:
            if not set(db_keys).issubset(set(altkeys.keys())):
                _logger.error(f"Alternative keys must contain all of the column names!")
                raise ValueError(f"Alternative keys must contain all of the column names!")
            
            db_keys = [altkeys[key] for key in db_keys]

        info_tup = zip(db_keys, info_keys)

        value_tups = []
        for col, info in info_tup:
            if info is not None:
                value_tups.append((col, self.__info[info]))
            else:
                value_tups.append((col, None))

        value_dict = dict(value_tups)

        value_dict[db_keys[0]] = self.__ticker
        value_dict[db_keys[1]] = np.datetime64('today', 'D')

        return value_dict
    
    def history(self, start_date: np.datetime64, end_date: np.datetime64, colkeys: dict[str, str] = None) -> pd.DataFrame:
        """Method for accessing the (daily) price and volume history for the stock. The columns of
        interest should be defined in the colkeys kwarg. That is the keys in colkeys dictionary
        should be the column names in the returned pandas DataFrame and the values the associated
        column names in the API. If None all columns will be returned with original column names.

        :param start_date: The start of the interval of interest
        :type start_date: np.datetime64
        :param end_date: The end of the interval of interest
        :type end_date: np.datetime64
        :param colkeys: The column key dictionary for the API. Defaults to None
        :type colkeys: dict[str, str], optional

        :raises ValueError: Raised if any of the given column keys is not present in the DataFrame columns

        :return: DataFrame containing the wanted history
        :rtype: pd.DataFrame
        """
        valid_start = strdate(start_date)
        valid_end = strdate(end_date)

        hist = self.__yfTicker.history(start=valid_start, end=valid_end)

        if colkeys is not None:
            if not set(colkeys.values()).issubset(set(hist.columns)):
                _logger.error(f"Invalid column keys provided!")
                raise ValueError(f"Invalid column keys provided!")
            
            hist = hist[list(colkeys.values())]
            hist.columns = list(colkeys.keys())
       
        return hist
    
    def income_statement(self, altkeys: dict[str, str] = None) -> pd.DataFrame:
        """Method for accessing the income statement for the stock. The basic information
        is defined as the column values for the incomeStmt table (see README or schema.py) columns
        "totRevenue" onwards. If some of the information cannot be reached the value will default
        to None. The keys in the returned dictionary will be the column names for the stock table
        unless alternative keys are passed as a kwarg.

        :param altkeys: Alternative keys as a dictionary of form column name -> alternative key \
                        Defaults to None.
        :type altkeys: dict[str, str], optional

        :raises ValueError: Raised if the alternative keys don't contain all of the column names as keys.

        :return: DataFrame with the keys as columns and rows containing the associated values for each \
                 reporting date. Index is the reporting dates.
        :rtype: pandas.DataFrame
        """
        # Due to the naming convention we can just retrieve the "name" values 
        # from incomeStmt_map as keys for Yahoo Finance API
        financial_keys = [incomeStmt_map[key]["name"] for key in incomeStmt_map.keys()]
        db_keys = list(incomeStmt_map.keys())

        # 'totRevenue' will be the first column of the actual income statement values.
        # So find it's index for later use
        statement_start = db_keys.index('totRevenue')

        if altkeys is not None:
            if not set(db_keys[statement_start:]).issubset(set(altkeys.keys())):
                _logger.error(f"Alternative keys must contain all of the column names!")
                raise ValueError(f"Alternative keys must contain all of the column names!")

            db_keys = [altkeys[key] for key in db_keys]

        financial_tup = list(zip(db_keys, financial_keys))
        financials = self.__yfTicker.financials

        value_tups = []
        for col, financial in financial_tup[statement_start:]:
            try:
                row = financials.loc[[financial]]
            except KeyError:
                _logger.warning(f"Stock {self.__ticker} doesn't have financial information for field {financial} ({col})")
                value_tups.append((col, None))
            else:
                value_tups.append((col, row.values[0]))
        
        value_df = pd.DataFrame().from_dict(dict(value_tups))
        value_df.set_index(financials.columns.values)

        return value_df
    
    def balance_sheet(self, altkeys: dict[str, str] = None) -> pd.DataFrame:
        """Method for accessing the balance sheet for the stock. The basic information
        is defined as the column values for the balanceSheet table (see README or schema.py) columns
        "totAssets" onwards. If some of the information cannot be reached the value will default 
        to None. The keys in the returned dictionary will be the column names for the stock table ¨
        unless alternative keys are passed as a kwarg.

        :param altkeys: Alternative keys as a dictionary of form column name -> alternative key \
                        Defaults to None.
        :type altkeys: dict[str, str], optional

        :raises ValueError: Raised if the alternative keys don't contain all of the column names as keys.

        :return: DataFrame with the keys as columns and rows containing the associated values for each \
                 reporting date. Index is the reporting dates.
        :rtype: pandas.DataFrame
        """
        # Due to the naming convention we can just retrieve the "name" values 
        # from balanceSheet_map as keys for Yahoo Finance API
        balanceSheet_keys = [balanceSheet_map[key]["name"] for key in balanceSheet_map.keys()]
        db_keys = list(balanceSheet_map.keys())

        # 'totAssets' will be the first column of the actual balance sheet values.
        # So find it's index for later use
        statement_start = db_keys.index('totAssets')

        if altkeys is not None:
            if not set(db_keys[statement_start:]).issubset(set(altkeys.keys())):
                _logger.error(f"Alternative keys must contain all of the column names!")
                raise ValueError(f"Alternative keys must contain all of the column names!")

            db_keys = [altkeys[key] for key in db_keys]

        balanceSheet_tup = list(zip(db_keys, balanceSheet_keys))
        balanceSheet = self.__yfTicker.balance_sheet

        value_tups = []
        for col, financial in balanceSheet_tup[statement_start:]:
            try:
                row = balanceSheet.loc[[financial]]
            except KeyError:
                _logger.warning(f"Stock {self.__ticker} doesn't have financial information for field {financial} ({col})")
                value_tups.append((col, None))
            else:
                value_tups.append((col, row.values[0]))
        
        value_df = pd.DataFrame().from_dict(dict(value_tups))
        value_df.set_index(balanceSheet.columns.values)

        return value_df
    
    def cash_flow_statement(self, altkeys: dict[str, str] = None) -> pd.DataFrame:
        """Method for accessing the cash flow statement for the stock. The basic information
        is defined as the column values for the balanceSheet table (see README or schema.py) columns
        "opCashFlow" onwards. If some of the information cannot be reached the value will default 
        to None. The keys in the returned dictionary will be the column names for the stock table ¨
        unless alternative keys are passed as a kwarg.

        :param altkeys: Alternative keys as a dictionary of form column name -> alternative key \
                        Defaults to None.
        :type altkeys: dict[str, str], optional

        :raises ValueError: Raised if the alternative keys don't contain all of the column names as keys.

        :return: DataFrame with the keys as columns and rows containing the associated values for each \
                 reporting date. Index is the reporting dates.
        :rtype: pandas.DataFrame
        """
        # Due to the naming convention we can just retrieve the "name" values 
        # from cashFlowStmt_map as keys for Yahoo Finance API
        cashFlow_keys = [cashFlowStmt_map[key]["name"] for key in cashFlowStmt_map.keys()]
        db_keys = list(cashFlowStmt_map.keys())

        # 'opCashFlow' will be the first column of the actual balance sheet values.
        # So find it's index for later use
        statement_start = db_keys.index('opCashFlow')

        if altkeys is not None:
            if not set(db_keys[statement_start:]).issubset(set(altkeys.keys())):
                _logger.error(f"Alternative keys must contain all of the column names!")
                raise ValueError(f"Alternative keys must contain all of the column names!")

            db_keys = [altkeys[key] for key in db_keys]

        cashFlow_tup = list(zip(db_keys, cashFlow_keys))
        cashFlow = self.__yfTicker.cashflow

        value_tups = []
        for col, financial in cashFlow_tup[statement_start:]:
            try:
                row = cashFlow.loc[[financial]]
            except KeyError:
                _logger.warning(f"Stock {self.__ticker} doesn't have financial information for field {financial} ({col})")
                value_tups.append((col, None))
            else:
                value_tups.append((col, row.values[0]))
        
        value_df = pd.DataFrame().from_dict(dict(value_tups))
        value_df.set_index(cashFlow.columns.values)

        return value_df
    
    def option_value(self, strike: float, maturity: np.datetime64, type: str) -> float:
        """Method for accessing the value of an option of given strike price, maturity and
        type ('call' or 'put'). 

        :param strike: The strike price
        :type strike: float
        :param maturity: The maturity (date of contract expiration)
        :type maturity: np.datetime64
        :param type: The type of option. Alternatives are 'call' and 'put'
        :type type: str

        :raises ValueError: Raised if given strike, maturity or type is invalid

        :return: The option value
        :rtype: float
        """
        maturities = self.__yfTicker.options
        if strdate(maturity) not in maturities:
            _logger.error(f"No options found for maturity {maturity}!")
            raise ValueError(f"No options found for maturity {maturity}!")
        
        opt = self.__yfTicker.option_chain(maturity)

        if type == "call":
            opt = opt.calls
        elif type == "put":
            opt = opt.puts
        else:
            _logger.error(f"Invalid option type {type} given!")
            raise ValueError(f"Invalid option type {type} given!")
        
        try:
            value = opt.loc[opt["strike"] == strike]["lastPrice"].values[0]
        except IndexError:
            _logger.error(f"No options found for strike {strike}!")
            raise ValueError(f"No options found for strike {strike}!")

        return value
    
    def all_options(self, type: str) -> dict[str, float]:
        """Method for accessing the values of all options of given type ('call' or 'put'). 
        Note that this method returns an empty dictionary if no options were found

        :param type: The type of option. Alternatives are 'call' and 'put'
        :type type: str

        :raises ValueError: Raised if given type is invalid

        :return: Dictionary from the option symbol to its value
        :rtype: dict[str, float]
        """
        if type not in ["call", "put"]:
            _logger.error(f"Invalid option type {type} given!")
            raise ValueError(f"Invalid option type {type} given!")

        maturities = self.__yfTicker.options

        value_dict = {}
        for maturity in maturities:
            opt = self.__yfTicker.option_chain(maturity)

            if type == "call":
                opt = opt.calls
            else:
                opt = opt.puts

            symbols = opt["contractSymbol"].values
            prices = opt["lastPrice"].values

            value_dict.update(dict(zip(symbols, prices)))

        return value_dict
    
    def options_by_maturity(self, maturity: np.datetime64, type: str) -> dict[float, float]:
        """Method for accessing the values of all options of given maturity and
        type ('call' or 'put'). 

        :param maturity: The maturity (date of contract expiration)
        :type maturity: np.datetime64
        :param type: The type of option. Alternatives are 'call' and 'put'
        :type type: str

        :raises ValueError: Raised if given maturity or type is invalid

        :return: Dictionary from the strike price to the options value
        :rtype: dict[float, float]
        """
        maturities = self.__yfTicker.options
        if strdate(maturity) not in maturities:
            _logger.error(f"No options found for maturity {maturity}!")
            raise ValueError(f"No options found for maturity {maturity}!")
        
        opt = self.__yfTicker.option_chain(maturity)

        if type == "call":
            opt = opt.calls
        elif type == "put":
            opt = opt.puts
        else:
            _logger.error(f"Invalid option type {type} given!")
            raise ValueError(f"Invalid option type {type} given!")
        
        strikes = opt["strike"].values
        prices = opt["lastPrice"].values

        return dict(zip(strikes, prices))


# List the functions and variables accessible in other modules
__all__ = ["YahooAPI"]
