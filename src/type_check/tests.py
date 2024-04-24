"""
Unit tests for the 'validate' decorator present in type_check module.
The functions 'skip_validations' and 'skip_list_checks' are only tested
as a consequence of the tests on 'validate' decorator.

Note that valid type checking requires use of Python 3.9 or later. However
there is a check for this as well.
"""
import unittest
import logging
import typing
import numpy as np
import pandas as pd


# Configure the root Logger object. This needs to be done
# before importing modules using logging.
if __name__ == "__main__":
    logging.basicConfig(filename='type_check_tests.log', level=logging.DEBUG, force=True,
                        format="%(levelname)s: %(name)s - %(message)s")


from type_check import *


class TestTypeCheckFunctions(unittest.TestCase):
    
    def test_validate_01(self):
        skip_validations(skip=True, _force_change=True)

        @validate(castable=False)
        def test(param1: list[str]) -> None:
            return "ret"
        
        test(["test"])

    def test_validate_02(self):
        skip_validations(skip=True, _force_change=True)

        @validate(castable=True)
        def test(param1: set[str]) -> None:
            return "ret"
        
        test(["test"])


    def test_validate_03(self):
        skip_validations(skip=False, _force_change=True)
        
        @validate(castable=False)
        def test(param1: list[str]) -> str:
            return "ret"
        
        test(["test"])


    def test_validate_04(self):
        
        @validate(castable=True)
        def test(param1: set[str]) -> str:
            return "ret"
        
        test(["test"])

    def test_validate_05(self):
        
        @validate(castable=False)
        def test(param1: set[str]) -> str:
            return "ret"
        
        with self.assertRaises(AssertionError):
            test(["test"])

    def test_validate_06(self):
        
        @validate(castable=False)
        def test(param1: list[str]) -> int:
            return "ret"
        
        with self.assertRaises(AssertionError):
            test(["test"])
    
    def test_validate_07(self):
        
        @validate(castable=True)
        def test(param1: list[str]) -> int:
            return "ret"
        
        with self.assertRaises(AssertionError):
            test(["test"])

    def test_validate_08(self):
        
        @validate(castable=False)
        def test(param1: typing.Union[str, int]) -> str:
            return "ret"
        
        test(0)

    def test_validate_09(self):
        
        @validate(castable=True)
        def test(param1: typing.Union[str, int]) -> str:
            return "ret"
        
        test(0)

    def test_validate_10(self):
        
        @validate(castable=False)
        def test(param1: list[typing.Union[str, int]]) -> str:
            return "ret"
        
        test([0, "test"])

    def test_validate_11(self):
        
        @validate(castable=True)
        def test(param1: set[typing.Union[str, int]]) -> str:
            return "ret"
        
        test([0, "test"])

    def test_validate_12(self):
        
        @validate(castable=False)
        def test(param1: list[typing.Union[str, int]]) -> str:
            return "ret"
        
        with self.assertRaises(AssertionError):
            test([0, "test", None])

    def test_validate_13(self):
        
        @validate(castable=True)
        def test(param1: set[typing.Union[str, int]]) -> str:
            return "ret"
        
        test([0, "test", None])  # None is castable to str

    def test_validate_14(self):
        
        @validate(castable=False)
        def test(param1: set[typing.Union[float, int]]) -> str:
            return "ret"
        
        with self.assertRaises(AssertionError):
            test([0, 1.0, None])

    def test_validate_15(self):
        
        @validate(castable=False)
        def test(param1: list[typing.Union[np.ndarray[np.int_], int]]) -> str:
            return "ret"
        
        test([0, np.array([1, 2, 3])])

    def test_validate_16(self):
        
        @validate(castable=True)
        def test(param1: set[typing.Union[np.ndarray[np.int_], int]]) -> str:
            return "ret"
        
        test([0, np.array([1, 2, 3])])



if __name__ == '__main__':
    unittest.main()


__all__ = ["TestTypeCheckFunctions"]