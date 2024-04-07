"""
Unit tests for the functions present in config module. Some functions that are excluded from tests are:

  save_config

due to their innate simplicity and assumption that the library methods are well tested.

If an unforseen errors occur, it is important to remove all temporary config files that didn't end up getting
cleaned up. Otherwise, they will cause issues when rerunning the tests.

Note that while not best practice the test do depend on each other. Thus, they are labelled in 
alphabetical order (unittest library should execute them in this order). If tests end up failing
this is good to keep in mind.
"""
import configparser
import unittest
import logging
import os
import inspect
import atexit


# Configure the root Logger object. This needs to be done
# before importing modules using logging.
if __name__ == "__main__":
    logging.basicConfig(filename='config_tests.log', level=logging.INFO, force=True,
                        format="%(levelname)s: %(name)s - %(message)s")

from config import *


# We don't want to save the temporary config files at program termination
atexit.unregister(save_config)

# Template for the name of the temporary config files used by tests. The tests will append 
# the method name at the end
_tmp_config = "__tmp_config_"

# Function for deleting a file if it exists
def _delete_if_exists(path):
    if os.path.exists(path):
        os.remove(path)


class TestConfigFunctions(unittest.TestCase):

    def test_a_configure_1(self):
        config_file = _tmp_config + inspect.stack()[0][3] + ".ini"
        with self.assertRaises(ValueError):
            configure(config_file=config_file)
    
    def test_a_configure_2(self):
        config_file = _tmp_config + inspect.stack()[0][3] + ".ini"
        with self.assertRaises(ValueError):
            configure(config_file=config_file, reconfigure=True)

    def test_a_configure_3(self):
        config_file = _tmp_config + inspect.stack()[0][3] + ".ini"
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'param1': '1',
                             'param2': '2',
                             'param3': '3'}

        with open(config_file, 'w') as c:
            config.write(c)
        
        configure(config_file=config_file)
        _delete_if_exists(config_file)

    def test_a_configure_4(self):
        config_file = _tmp_config + inspect.stack()[0][3] + ".ini"
        with self.assertRaises(ValueError):
            configure(config_file=config_file)

    def test_a_configure_5(self):
        config_file = _tmp_config + inspect.stack()[0][3] + ".ini"
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'param1': '1',
                             'param2': '2',
                             'param3': '3'}

        with open(config_file, 'w') as c:
            config.write(c)
        
        configure(config_file=config_file, reconfigure=True, save_old=False)
        _delete_if_exists(config_file)

    def test_b_get_value_1(self):
        config_file = _tmp_config + inspect.stack()[0][3] + ".ini"
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'param1': '1',
                             'param2': '2',
                             'param3': '3'}

        with open(config_file, 'w') as c:
            config.write(c)
        
        configure(config_file=config_file, reconfigure=True, save_old=False)

        self.assertEqual(get_value("DEFAULT", "param1"), '1')
        _delete_if_exists(config_file)

    def test_b_get_value_2(self):
        config_file = _tmp_config + inspect.stack()[0][3] + ".ini"
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'param1': '1',
                             'param2': '2',
                             'param3': '3'}

        with open(config_file, 'w') as c:
            config.write(c)
        
        configure(config_file=config_file, reconfigure=True, save_old=False)

        with self.assertRaises(ValueError):
            get_value("TEST", "param1")

        _delete_if_exists(config_file)

    def test_b_get_value_3(self):
        config_file = _tmp_config + inspect.stack()[0][3] + ".ini"
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'param1': '1',
                             'param2': '2',
                             'param3': '3'}

        with open(config_file, 'w') as c:
            config.write(c)
        
        configure(config_file=config_file, reconfigure=True, save_old=False)

        with self.assertRaises(ValueError):
            get_value("DEFAULT", "param4")

        _delete_if_exists(config_file)

    def test_c_set_value_1(self):
        config_file = _tmp_config + inspect.stack()[0][3] + ".ini"
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'param1': '1',
                             'param2': '2',
                             'param3': '3'}

        with open(config_file, 'w') as c:
            config.write(c)
        
        configure(config_file=config_file, reconfigure=True, save_old=False)
        set_value("DEFAULT", "param1", '99')

        self.assertEqual(get_value("DEFAULT", "param1"), '99')
        _delete_if_exists(config_file)

    def test_c_set_value_2(self):
        config_file = _tmp_config + inspect.stack()[0][3] + ".ini"
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'param1': '1',
                             'param2': '2',
                             'param3': '3'}

        with open(config_file, 'w') as c:
            config.write(c)
        
        configure(config_file=config_file, reconfigure=True, save_old=False)

        with self.assertRaises(ValueError):
            set_value("TEST", "param1", '99')

        _delete_if_exists(config_file)

    def test_c_set_value_3(self):
        config_file = _tmp_config + inspect.stack()[0][3] + ".ini"
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'param1': '1',
                             'param2': '2',
                             'param3': '3'}

        with open(config_file, 'w') as c:
            config.write(c)
        
        configure(config_file=config_file, reconfigure=True, save_old=False)
        set_value("DEFAULT", "param4", '99')

        self.assertEqual(get_value("DEFAULT", "param4"), '99')
        _delete_if_exists(config_file)
    
    def test_c_set_value_4(self):
        config_file = _tmp_config + inspect.stack()[0][3] + ".ini"
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'param1': '1',
                             'param2': '2',
                             'param3': '3'}

        with open(config_file, 'w') as c:
            config.write(c)
        
        configure(config_file=config_file, reconfigure=True, save_old=False)

        with self.assertRaises(ValueError):
            set_value("DEFAULT", "param4", '99', allow_new_keys=False)

        _delete_if_exists(config_file)



if __name__ == '__main__':
    unittest.main()


__all__ = ["TestConfigFunctions"]
