"""
Unit tests for most of the API methods present in stockAPI module

The tests should be ran from the src directory
"""
import unittest
import numpy as np
import pandas as pd


if __name__ == "__main__":
    raise RuntimeError(f"The tests for stockAPI module needs to be run from src directory!")

from stock.schema import *
from stock.stockAPI import *

# Rename the API of interest for testing
TestAPI = YahooAPI


class TestAPIMethods(unittest.TestCase):

    def test_a_init_1(self):
        TestAPI("AAPL")

    def test_a_init_2(self):
        TestAPI("NDA-FI.HE")

    def test_a_init_3(self):
        with self.assertRaises(ValueError):
            TestAPI("SPY")

    def test_a_init_4(self):
        with self.assertRaises(ValueError):
            TestAPI("TEST TICKER")

    def test_b_description_1(self):
        aapl = TestAPI("AAPL")
        self.assertIsInstance(aapl.description(), str)

    def test_b_description_2(self):
        nda = TestAPI("NDA-FI.HE")
        self.assertIsInstance(nda.description(), str)

    def test_c_summary_1(self):
        aapl = TestAPI("AAPL")
        self.assertIsInstance(aapl.summary(), dict)

    def test_c_summary_2(self):
        db_keys = list(stock_map.keys())

        aapl = TestAPI("AAPL")
        self.assertListEqual(list(aapl.summary().keys()), db_keys)

    def test_c_summary_3(self):
        db_keys = list(stock_map.keys())
        alt_keys = db_keys.copy()
        alt_keys[2] = "testKey"
        altkey_dict = dict(zip(db_keys, alt_keys))

        aapl = TestAPI("AAPL")
        self.assertListEqual(list(aapl.summary(altkeys=altkey_dict).keys()), alt_keys)

    def test_c_summary_4(self):
        aapl = TestAPI("AAPL")
        self.assertIsInstance(aapl.summary()["PE"], float)

    def test_c_summary_5(self):
        aapl = TestAPI("AAPL")
        self.assertIsNone(aapl.summary()["drift"])

    def test_d_history_1(self):
        aapl = TestAPI("AAPL")
        self.assertIsInstance(aapl.history("2020", "2021"), pd.DataFrame)

    def test_d_history_2(self):
        # These are set for Yahoo API, might need to be changed for other APIs
        colkeys = {"Price": "Close", "Volume": "Volume"}

        aapl = TestAPI("AAPL")
        hist = aapl.history("2020", "2021", colkeys=colkeys)

        self.assertListEqual(list(hist.columns), list(colkeys.keys()))

    def test_d_history_3(self):
        # These are set for Yahoo API, might need to be changed for other APIs
        colkeys = {"Price": "Clo", "Volume": "Volume"}

        aapl = TestAPI("AAPL")

        with self.assertRaises(ValueError):
            aapl.history("2020", "2021", colkeys=colkeys)

    def test_e_income_statement_1(self):
        aapl = TestAPI("AAPL")
        self.assertIsInstance(aapl.income_statement(), pd.DataFrame)

    def test_e_income_statement_2(self):
        nda = TestAPI("NDA-FI.HE")
        self.assertIsInstance(nda.income_statement(), pd.DataFrame)

    def test_e_income_statement_3(self):
        aapl = TestAPI("AAPL")
        self.assertIsInstance(aapl.income_statement()["costRevenue"], pd.Series)

    def test_e_income_statement_4(self):
        db_keys = list(incomeStmt_map.keys())

        aapl = TestAPI("AAPL")
        self.assertListEqual(list(aapl.income_statement().columns), db_keys[4:])

    def test_e_income_statement_5(self):
        financial_keys = [incomeStmt_map[key]["name"] for key in incomeStmt_map.keys()]
        db_keys = list(incomeStmt_map.keys())

        altkeys = dict(zip(db_keys, financial_keys))

        aapl = TestAPI("AAPL")
        self.assertListEqual(list(aapl.income_statement(altkeys=altkeys).columns), financial_keys[4:])

    def test_f_balance_sheet_1(self):
        aapl = TestAPI("AAPL")
        self.assertIsInstance(aapl.balance_sheet(), pd.DataFrame)

    def test_f_balance_sheet_2(self):
        nda = TestAPI("NDA-FI.HE")
        self.assertIsInstance(nda.balance_sheet(), pd.DataFrame)

    def test_f_balance_sheet_3(self):
        aapl = TestAPI("AAPL")
        self.assertIsInstance(aapl.balance_sheet()["totAssets"], pd.Series)

    def test_f_balance_sheet_4(self):
        db_keys = list(balanceSheet_map.keys())

        aapl = TestAPI("AAPL")
        self.assertListEqual(list(aapl.balance_sheet().columns), db_keys[4:])

    def test_f_balance_sheet_5(self):
        balanceSheet_keys = [balanceSheet_map[key]["name"] for key in balanceSheet_map.keys()]
        db_keys = list(balanceSheet_map.keys())

        altkeys = dict(zip(db_keys, balanceSheet_keys))

        aapl = TestAPI("AAPL")
        self.assertListEqual(list(aapl.balance_sheet(altkeys=altkeys).columns), balanceSheet_keys[4:])

    def test_g_cash_flow_statement_1(self):
        aapl = TestAPI("AAPL")
        self.assertIsInstance(aapl.cash_flow_statement(), pd.DataFrame)

    def test_g_cash_flow_statement_2(self):
        nda = TestAPI("NDA-FI.HE")
        self.assertIsInstance(nda.cash_flow_statement(), pd.DataFrame)

    def test_g_cash_flow_statement_3(self):
        aapl = TestAPI("AAPL")
        self.assertIsInstance(aapl.cash_flow_statement()["issCap"], pd.Series)

    def test_g_cash_flow_statement_4(self):
        db_keys = list(cashFlowStmt_map.keys())

        aapl = TestAPI("AAPL")
        self.assertListEqual(list(aapl.cash_flow_statement().columns), db_keys[4:])

    def test_g_cash_flow_statement_5(self):
        cashFlow_keys = [cashFlowStmt_map[key]["name"] for key in cashFlowStmt_map.keys()]
        db_keys = list(cashFlowStmt_map.keys())

        altkeys = dict(zip(db_keys, cashFlow_keys))

        aapl = TestAPI("AAPL")
        self.assertListEqual(list(aapl.cash_flow_statement(altkeys=altkeys).columns), cashFlow_keys[4:])

    def test_h_all_options_1(self):
        aapl = TestAPI("AAPL")
        self.assertIsInstance(aapl.all_options("call"), dict)

    def test_h_all_options_2(self):
        aapl = TestAPI("AAPL")
        self.assertIsInstance(aapl.all_options("put"), dict)

    def test_h_all_options_3(self):
        nda = TestAPI("NDA-FI.HE")
        self.assertIsInstance(nda.all_options("put"), dict)
    
    def test_h_all_options_4(self):
        aapl = TestAPI("AAPL")
        with self.assertRaises(ValueError):
            aapl.all_options("test")

    def test_i_option_value_1(self):
        aapl = TestAPI("AAPL")
        symbol = list(aapl.all_options("call").keys())[0]
        maturity = f"20{symbol[4:6]}-{symbol[6:8]}-{symbol[8:10]}"
        strike = float(symbol[11:16])

        self.assertIsInstance(aapl.option_value(strike, maturity, "call"), float)

    def test_i_option_value_2(self):
        aapl = TestAPI("AAPL")
        symbol = list(aapl.all_options("call").keys())[0]
        maturity = f"20{symbol[4:6]}-{symbol[6:8]}-{symbol[8:10]}"
        strike = float(symbol[11:16])

        with self.assertRaises(ValueError):
            aapl.option_value(strike, np.datetime64(maturity) + 1, "call")

    def test_i_option_value_3(self):
        aapl = TestAPI("AAPL")
        symbol = list(aapl.all_options("call").keys())[0]
        maturity = f"20{symbol[4:6]}-{symbol[6:8]}-{symbol[8:10]}"
        strike = float(symbol[11:16])

        with self.assertRaises(ValueError):
            aapl.option_value(strike + 1, maturity, "call")

    def test_i_option_value_4(self):
        aapl = TestAPI("AAPL")
        symbol = list(aapl.all_options("call").keys())[0]
        maturity = f"20{symbol[4:6]}-{symbol[6:8]}-{symbol[8:10]}"
        strike = float(symbol[11:16])

        with self.assertRaises(ValueError):
            aapl.option_value(strike, maturity, "test")

    def test_j_options_by_maturity_1(self):
        aapl = TestAPI("AAPL")
        symbol = list(aapl.all_options("call").keys())[0]
        maturity = f"20{symbol[4:6]}-{symbol[6:8]}-{symbol[8:10]}"

        self.assertIsInstance(aapl.options_by_maturity(maturity, "call"), dict)

    def test_j_options_by_maturity_2(self):
        aapl = TestAPI("AAPL")
        symbol = list(aapl.all_options("call").keys())[0]
        maturity = f"20{symbol[4:6]}-{symbol[6:8]}-{symbol[8:10]}"

        with self.assertRaises(ValueError):
            aapl.options_by_maturity(maturity, "test")

    def test_j_options_by_maturity_3(self):
        aapl = TestAPI("AAPL")
        symbol = list(aapl.all_options("call").keys())[0]
        maturity = f"20{symbol[4:6]}-{symbol[6:8]}-{symbol[8:10]}"

        with self.assertRaises(ValueError):
            aapl.options_by_maturity(np.datetime64(maturity) + 1, "call")


__all__ = ["TestAPIFunctions"]
