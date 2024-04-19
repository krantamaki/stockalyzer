"""
Main script for running the tests in the modules. The tests themselves are
located in the modules themselves in tests.py file. We allow running the tests
for either all modules or for some subset of modules by setting valid command line
arguments. The args are

  -a (--all): for running all tests
  -d (--db): for running tests in the db module
  -c (--config): for running tests in the config module
  -s (--stock): for running tests in the whole stock module
  -f (--financial_reporting): for running tests in the financial reporting submodule
  -p (--stockAPI): for running tests in the stockAPI submodule
  -w (--web_app): for running tests in the web_app module
  -l (--cmd_app): for running tests in the cmd_app module

For example to test the db and config modules run (in src directory)
  > python3 run_tests.py -d -c 
"""
import logging
import unittest
import argparse
import sys


# Configure the root Logger object. This needs to be done
# before importing modules using logging.
if __name__ == "__main__":
    logging.basicConfig(filename='test.log', level=logging.INFO, force=True,
                        format="%(levelname)s: %(name)s - %(message)s")

# Import the test cases
from db.tests import TestDatabaseFunctions
from config.tests import TestConfigFunctions
from stock.stockAPI.tests import TestAPIMethods

test_map = {"db": TestDatabaseFunctions,
            "config": TestConfigFunctions,
            "stockAPI": TestAPIMethods}


# Function for loading tests from a given module
def load_tests_from_module(module, loader):
    test_class = test_map[module]
    return loader.loadTestsFromTestCase(test_class)


# Simple function for parsing the command line arguments
def parse_cmd():
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--all', action="store_true")
    parser.add_argument('-d', '--db', action="store_true")
    parser.add_argument('-c', '--config', action="store_true")
    parser.add_argument('-s', '--stock', action="store_true")
    parser.add_argument('-f', '--financial_reporting', action="store_true")
    parser.add_argument('-p', '--stockAPI', action="store_true")
    parser.add_argument('-w', '--web_app', action="store_true")
    parser.add_argument('-l', '--cmd_app', action="store_true")
    
    args = parser.parse_args()

    return vars(args)


def main():
    if len(sys.argv) <= 1:
        logging.error("No tests were specified!")
        raise RuntimeError("No tests were specified!")
    
    args = parse_cmd()
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    if args['all']:
        for module in test_map:
            suite.addTest(load_tests_from_module(module, loader))
    else:
        if args['db']:
            suite.addTest(load_tests_from_module('db', loader))
        if args['config']:
            suite.addTest(load_tests_from_module('config', loader))
        if args['stockAPI']:
            suite.addTest(load_tests_from_module('stockAPI', loader))

    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == "__main__":
    main()
