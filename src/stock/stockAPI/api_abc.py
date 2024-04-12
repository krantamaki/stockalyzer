"""
Abstract base class declaring the template that all API classes should follow. This should guarantee
that even if different sources for data were used the software should work with minimal changes.
The methods here have a minimal description and a more thorough one should be provided by the actual
API class.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np


class abcAPI(ABC):

    # We should be able to initialize the API object with just the ticker symbol
    @abstractmethod
    def __init__(self, ticker: str) -> None:
        pass

    # We require that we can access a description for the underlying
    @abstractmethod
    def description(self) -> str:
        pass

    # We require that we can access summary statistics like beta, P/E etc.
    # Additionally, we should be able to provide alternative keys for the columns
    @abstractmethod
    def summary(self, altkeys: dict[str, str] = None) -> dict[str, any]:
        pass

    # We should be able to retrieve the history of the share price, volume etc.
    # Again we should be able to provide alternative keys for the columns
    @abstractmethod
    def history(self, start_date: np.datetime64, end_date: np.datetime64,
                altkeys: dict[str, str] = None) -> pd.DataFrame:
        pass

    # We should be able to retrieve the income statement for the underlying
    @abstractmethod
    def income_statement(self, altkeys: dict[str, str] = None) -> pd.DataFrame:
        pass

    # We should be able to retrieve the balance sheet for the underlying
    @abstractmethod
    def balance_sheet(self, altkeys: dict[str, str] = None) -> pd.DataFrame:
        pass

    # We should be able to retrieve the cash flow statement for the underlying
    @abstractmethod
    def cash_flow_statement(self, altkeys: dict[str, str] = None) -> pd.DataFrame:
        pass
    
    # We should be able to retrieve the value of an option for some given strike
    # and maturity, if such exists
    @abstractmethod
    def option_value(self, strike: float, maturity: np.datetime64, type: str) -> float:
        pass

    # We should be able to retrieve the values of all available options (of a given type) 
    # as dictionary from the option symbol to the option value
    @abstractmethod
    def all_options(self, type: str) -> dict[str, float]:
        pass

    # We should be able to retrieve the values of all available options for a given maturity 
    # as dictionary from the strike to the option value
    @abstractmethod
    def options_by_maturity(self, maturity: np.datetime64, type: str) -> dict[float, float]:
        pass
    