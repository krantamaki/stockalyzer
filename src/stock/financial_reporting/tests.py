"""
Unit tests for most of the functions and methods present in financial_reporting module

Separate TestCase objects are implemented for each submodule
"""
import unittest
import numpy as np
import pandas as pd
import warnings


# Ignore potential warnings
warnings.filterwarnings("ignore")


if __name__ == "__main__":
    raise RuntimeError(f"The tests for financial_reporting module needs to be run from src directory!")

from stock.financial_reporting import *


class TestStatementRowMethods(unittest.TestCase):
    
    def test_a_init_1(self):
        values = np.array([1, 2, 3, 4])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        StatementRow("test", values, dates)

    def test_a_init_2(self):
        values = np.array([1, 2, 3])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        with self.assertRaises(ValueError):
            StatementRow("test", values, dates)

    def test_a_init_3(self):
        values = np.array([1, 2, 3])
        dates = ['01-01-2020', '01-01-2021', '01-01-2022']
        with self.assertRaises(ValueError):
            StatementRow("test", values, dates)

    def test_a_init_4(self):
        values = []
        dates = []
        StatementRow("test", values, dates)

    def test_b_getitem_1(self):
        values = np.array([1, 2, 3, 4])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        row = StatementRow("test", values, dates)

        self.assertEqual(1, row['2020'])

    def test_b_getitem_2(self):
        values = np.array([1, 2, 3, 4])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        row = StatementRow("test", values, dates)

        with self.assertRaises(KeyError):
            row['2019']

    def test_b_getitem_3(self):
        values = np.array([1, 2, 3, 4])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        row = StatementRow("test", values, dates)

        with self.assertRaises(KeyError):
            row['2021-01-02']

    def test_c_setitem_1(self):
        values = np.array([1, 2, 3, 4])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        row = StatementRow("test", values, dates)
        row['2020'] = -1

        self.assertEqual(-1, row['2020'])

    def test_c_setitem_2(self):
        values = np.array([1, 2, 3, 4])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        row = StatementRow("test", values, dates)
        row['2019'] = -1

        self.assertEqual(-1, row['2019'])

    def test_c_setitem_3(self):
        values = np.array([1, 2, 3, 4])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        row = StatementRow("test", values, dates)
        row['2021-01-02'] = -1

        self.assertEqual(-1, row['2021-01-02'])

    def test_d_iget_1(self):
        values = np.array([1, 2, 3, 4])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        row = StatementRow("test", values, dates)

        self.assertEqual((dates[-1], values[-1]), row.iget(0))

    def test_d_iget_2(self):
        values = np.array([1, 2, 3, 4])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        row = StatementRow("test", values, dates)

        self.assertEqual((dates[0], values[0]), row.iget(-1))

    def test_d_iget_3(self):
        values = np.array([1, 2, 3, 4])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        row = StatementRow("test", values, dates)
        
        with self.assertRaises(KeyError):
            row.iget(5)

    def test_e_values(self):
        values = np.array([1, 2, 3, 4])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        row = StatementRow("test", values, dates)

        self.assertListEqual(list(np.flip(values)), list(row.values()))

    def test_e_dates(self):
        values = np.array([1, 2, 3, 4])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        row = StatementRow("test", values, dates)

        self.assertListEqual(list(np.flip(dates)), list(row.dates()))

    def test_f_mean(self):
        values = np.array([1, 2, 1, 2])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        row = StatementRow("test", values, dates)
        
        self.assertAlmostEquals(1.5, row.mean())

    def test_f_std(self):
        values = np.array([1, 1, 1, 1])
        dates = np.array(['2020', '2021', '2022', '2023'], dtype="datetime64[D]")
        row = StatementRow("test", values, dates)
        
        self.assertAlmostEquals(0, row.std())

    def test_g_predict_1(self):
        dates = np.array([1, 2, 3, 4], dtype="datetime64[D]")
        values = np.array([1, 2, 3, 4])
        row = StatementRow("test", values, dates)

        predicted = row.predict(n_predictions=3, func="linear")
        exact = np.array([5, 6, 7])
        
        self.assertTrue(np.isclose(predicted, exact, atol=1e-3).all())

    def test_g_predict_2(self):
        dates = np.array([1, 2, 3, 4], dtype="datetime64[D]")
        values = np.exp([1, 2, 3, 4])
        row = StatementRow("test", values, dates)

        predicted = row.predict(n_predictions=3, func="exponential")
        exact = np.exp([5, 6, 7])
        
        self.assertTrue(np.isclose(predicted, exact, atol=1e-3).all())

    def test_g_predict_3(self):
        dates = np.array([1, 2, 3, 4], dtype="datetime64[D]")
        values = np.log([1, 2, 3, 4])
        row = StatementRow("test", values, dates)

        predicted = row.predict(n_predictions=3, func="logarithmic")
        exact = np.log([5, 6, 7])
        
        self.assertTrue(np.isclose(predicted, exact, atol=1e-3).all())

    def test_g_predict_4(self):
        # Free cash flow of AAPL from 2020 to 2022 (not exact dates)
        values = np.array([92_953_000_000, 111_443_000_000, 99_584_000_000])
        dates = np.array(['2021', '2022', '2023'])
        row = StatementRow("AAPL FCF", values, dates)

        predicted = row.predict(n_predictions=3, func="linear")

        self.assertTrue(np.isfinite(predicted).all())

    def test_g_predict_5(self):
        # Free cash flow of AAPL from 2020 to 2022 (not exact dates)
        values = np.array([92_953_000_000, 111_443_000_000, 99_584_000_000])
        dates = np.array(['2021', '2022', '2023'])
        row = StatementRow("AAPL FCF", values, dates)

        predicted = row.predict(n_predictions=3, func="exponential")
        
        self.assertTrue(np.isfinite(predicted).all())

    def test_g_predict_6(self):
        # Free cash flow of AAPL from 2020 to 2022 (not exact dates)
        values = np.array([92_953_000_000, 111_443_000_000, 99_584_000_000])
        dates = np.array(['2021', '2022', '2023'])
        row = StatementRow("AAPL FCF", values, dates)

        predicted = row.predict(n_predictions=3, func="logarithmic")
        
        self.assertTrue(np.isfinite(predicted).all())

    def test_h_custom_predict_1(self):
        
        def test_func(x, a, b):
            return a * x + b

        dates = np.array([1, 2, 3, 4], dtype="datetime64[D]")
        values = np.array([1, 2, 3, 4])
        row = StatementRow("test", values, dates)

        predicted = row.custom_predict(test_func, n_predictions=3)
        exact = np.array([5, 6, 7])
        
        self.assertTrue(np.isclose(predicted, exact, atol=1e-3).all())

    def test_h_custom_predict_2(self):
        
        def test_func(x, a, b):
            return a * np.exp(b * x)

        dates = np.array([1, 2, 3, 4], dtype="datetime64[D]")
        values = np.exp([1, 2, 3, 4])
        row = StatementRow("test", values, dates)

        predicted = row.custom_predict(test_func, init_params=[1, 0.1], n_predictions=3)
        exact = np.exp([5, 6, 7])
        
        self.assertTrue(np.isclose(predicted, exact, atol=1e-3).all())


__all__ = ["TestStatementRowMethods"]
