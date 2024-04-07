"""
Module for handling the configuration information. 

Note that the configuration options should be set in the config.ini file
(or some other config file, but we should mainly use config.ini).
No code here should be altered by the user.

Note for this code to function correctly, the code using it must be ran from
the src directory.
"""
import configparser
import logging
import atexit
from pathlib import Path


# We use Pythons logging library to control and redirect our outputs.
# To this end be need to define the Logger object
_logger = logging.getLogger(__name__)

# We will store the used ConfigParser object in global scope
_config = None

# Path to the current config file
_config_path = None


def save_config() -> None:
    """Function for saving the current instance of ConfigParser

    :return: Void
    :rtype: None
    """
    if _config is None:
        return
    
    with open(_config_path, 'w') as config_file:
        _config.write(config_file)

# We will save the config file at program termination
atexit.register(save_config)


def configure(config_file: str = "config.ini", reconfigure: bool = False, save_old: bool = True) -> None:
    """Function for reading a given config file and storing the information
    in a ConfigParser object for later use. Config file should be of .ini format
    that Pythons standard library configparser can read.

    :param config_file: Path to the config file to be read. Defaults to "config.ini".
    :type config_file: str, optional
    :param reconfigure: Boolean flag telling if the existing config information should be \
                        replaced by new one read from given config_file. Defaults to False
    :type reconfigure: bool, optional
    :param save_old: Boolean flag telling if the possible changes to the old configure file \
                     should be saved before changing to the new one. Defaults to True
    :type save_old: bool, optional

    :raises ValueError: Raised if config file not found or tried to reconfigure without setting \
                        reconfigure kwarg to True

    :return: Void
    :rtype: None
    """
    global _config, _config_path

    if Path(config_file).is_file():
        if _config is not None:
            if reconfigure is False:
                _logger.error(f"Tried to configure with file {config_file}, when program already configured with {_config_path}!")
                raise ValueError(f"Tried to configure with file {config_file}, when program already configured with {_config_path}!")
            else:
                if _config_path == config_file:
                    _logger.warning(f"Reloading the configure file during program execution is not recommended!")
                else:
                    _logger.warning(f"Changing the config file during program execution is not recommended! (Changing from {_config_path} to {config_file})")
                    if save_old:
                        save_config()

        _config = configparser.ConfigParser()
        _config.read(config_file)
        _config_path = config_file

    else:
        _logger.error(f"Invalid configuration file {config_file} passed!")
        raise ValueError(f"Invalid configuration file {config_file} passed!")
    


def get_value(section: str, key: str) -> any:
    """Function for accessing a value by section name and key from the config file

    :param section: Name of the section from where the key is looked for
    :type section: str
    :param key: The key in the section for the value
    :type key: str

    :raises ValueError: Raised if invalid section name or key is passed

    :return: The retrieved value
    :rtype: any
    """
    try:
        value = _config[section][key]
    except KeyError:
        _logger.error(f"Invalid key {key} for section {section} passed!")
        raise ValueError(f"Invalid key {key} for section {section} passed!")
    else:
        return value


def set_value(section: str, key: str, value: any, allow_new_keys: bool = True) -> None:
    """Function for setting a value by section name and key for the config file

    :param section: Name of the section from where the key is looked for
    :type section: str
    :param key: The key in the section for the value
    :type key: str
    :param value: The value to be set
    :type value: any
    :param allow_new_keys: Boolean flag telling if setting value to a previously unspecified \
                           key is allowed. Defaults to True
    :type allow_new_keys: bool, optional

    :raises ValueError: Raised if invalid section name or key is passed

    :return: Void
    :rtype: None
    """
    try:
        _config[section]
    except KeyError:
        _logger.error(f"Invalid section {section} passed!")
        raise ValueError(f"Invalid for section {section} passed!")
    else:
        if key not in _config[section]:
            if not allow_new_keys:
                _logger.error(f"Tried to create a new key {key} for section {section}!")
                raise ValueError(f"Tried to create a new key {key} for section {section}!")
            _logger.warning(f"New key {key} made for section {section}!")

        _config[section][key] = value

# List the functions and variables accessible in other modules
__all__ = ["save_config", "configure", "get_value", "set_value"]
