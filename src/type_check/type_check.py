"""
Module defining decorators for static type checking.

Note that type subscription requires Python 3.9 or later!
"""
from __future__ import annotations
from typing import get_type_hints, Union, _UnionGenericAlias
from types import GenericAlias
import numpy as np
import sys
import logging


# We use Pythons logging library to control and redirect our outputs.
# To this end be need to define the Logger object
_logger = logging.getLogger(__name__)


# Global variable holding the info on whether the validations should be skipped
# Accessible by the skip_validations function
_skip_validations = None


# Global variable holding the info on if type of element in list should be validated
# This requires doing isinstance check on all elements in the list and is thus a
# very expensive operation
_skip_array_checks = None


def _min_python_satisfied() -> bool:
    """Function that checks that the minimum Python version is satisfied.
    The minimum version is Python 3.9, which first implemented type subscription.

    :return: True if minimum version is satisfied, False otherwise
    :rtype: bool
    """
    return sys.version_info >= (3, 9)


def _is_castable(value: any, type_hint: any) -> bool:
    """Function that checks that a given value can be cast as given type.
    
    :return: True if value is castable, False otherwise
    :rtype: bool
    """
    if not callable(type_hint):
        return False
    try:
        type_hint(value)
    except Exception:
        return False
    return True


def _type_check(value: any, type_hint: any, castable: bool = True) -> bool:
    """Function for checking that the type is satisfied.
    Note that for more complex types the checks might not be most exchaustive. The supported
    subscriptable types are: 'list', 'set', 'dict', 'tuple', 'typing.Union', 'numpy.ndarray'
    See the README in the 'type_check' module for more information.

    :param value: The value to be checked
    :type value: any
    :param type_hint: The type that was hinted
    :type type_hint: any
    :param castable: Boolean flag telling if the check should be made for exact types, or is it \
                     enough that the value is castable to the given type. Defaults to True.
    :type castable: bool, optional

    :return: True if value matches the type hint, False otherwise
    :rtype: bool
    """

    if castable:
        check_func = _is_castable
    else:
        check_func = isinstance

    if type_hint == any:
        return True
    
    if type_hint is None:
        return value == None

    if type_hint == callable:
        return callable(value)
    
    # Check if type hint indicates a more complicated type
    # Note depending on the input this might fail
    if isinstance(type_hint, (GenericAlias, _UnionGenericAlias)):

        if type_hint.__origin__ == Union:
            return bool(sum([int(_type_check(value, arg, castable=castable)) for arg in type_hint.__args__]))

        if check_func(value, list) and type_hint.__origin__ == list:
            if skip_array_checks():
                return True
            else:
                for elem in value:
                    if not sum([int(_type_check(elem, arg, castable=castable)) for arg in type_hint.__args__]):
                        _logger.debug(f"Element {elem} doesn't match any of the argument types {type_hint.__args__}!")
                        return False
                return True  # Note that if the list is empty this will return True

        elif check_func(value, set) and type_hint.__origin__ == set:
            if skip_array_checks():
                return True
            else:
                for elem in value:
                    if not sum([int(_type_check(elem, arg, castable=castable)) for arg in type_hint.__args__]):
                        _logger.debug(f"Element {elem} doesn't match any of the argument types {type_hint.__args__}!")
                        return False
                return True  # Note that if the set is empty this will return True

        elif check_func(value, np.ndarray) and type_hint.__origin__ == np.ndarray:
            # Note that we assume that the type of the numpy array is something that can cast the value 1
            if bool(sum([int(_type_check(value.dtype.type(1), arg)) for arg in type_hint.__args__])):
                return True
            else:
                _logger.debug(f"Value {value} doesn't match the type hint {type_hint}!")
                return False
        
        elif check_func(value, dict) and type_hint.__origin__ == dict:
            if skip_array_checks():
                return True
            else:
                if not len(type_hint.__args__) == 2:
                    _logger.debug(f"Invalid number of argument types {type_hint.__args__}!")
                    return False
                for tup in list(dict(value).items()):
                    if not (_type_check(tup[0], type_hint.__args__[0], castable=castable) and
                            _type_check(tup[1], type_hint.__args__[1], castable=castable)):
                        _logger.debug(f"Element {elem} doesn't match any of the argument types {type_hint.__args__}!")
                        return False
                return True  # Note that if the dict is empty this will return True
            
        elif check_func(value, tuple) and type_hint.__origin__ == tuple:
            if len(value) != len(type_hint.__args__):
                _logger.debug(f"Invalid number of argument types {type_hint.__args__}!")
                return False
            
            for elem, arg in zip(value, type_hint.__args__):
                if not _type_check(elem, arg, castable=castable):
                    _logger.debug(f"Element {elem} doesn't match the argument type {arg}!")
                    return False
            return True

        # Default to a simple check
        else:
            if check_func(value, type_hint.__origin__):
                return True
            else:
                _logger.debug(f"Value {value} doesn't match the type hint {type_hint}!")
                return False

    else:
        if check_func(value, type_hint):
            return True
        else:
            _logger.debug(f"Value {value} doesn't match the type hint {type_hint}!")
            return False


def skip_validations(skip: bool = False, _force_change: bool = False) -> None:
    """Function that determines if validations should be skipped. If the validations are
    skipped some overhead might be reduced, but with the cost of possible undefined behavior.

    :param skip: Boolean telling if the validation skips should be performed. Defaults to False
    :type skip: bool, optional
    :param _force_change: Boolean flag telling if changing the set setting should be forced. Mainly for debugging \
                          and testing purposes. Defaults to False
    :type _force_change: bool, optional

    :raises AssertationError: Raised if invalid type of argument passed

    :return: Void
    :rtype: None
    """
    global _skip_validations

    if _skip_validations is None:
        if not isinstance(skip, bool):
            _logger.error(f"Invalid argument type {type(skip)} passed to function skip_validations. (bool required)")
            raise AssertionError(f"Invalid argument type {type(skip)} passed to function skip_validations. (bool required)")
        _skip_validations = skip

    elif _force_change:
        if not isinstance(skip, bool):
            _logger.error(f"Invalid argument type {type(skip)} passed to function skip_validations. (bool required)")
            raise AssertionError(f"Invalid argument type {type(skip)} passed to function skip_validations. (bool required)")
        
        _logger.warning("Changing the settings for the type_check module during program execution not recommended!")
        _skip_validations = skip
    
    return _skip_validations


def skip_array_checks(skip: bool = False, _force_change: bool = False) -> None:
    """Function that determines if each element of an array should be checked for valid type. This understandably adds
    quite a lot of overhead. 

    :param skip: Boolean telling if the validation skips should be performed. Defaults to False
    :type skip: bool, optional
    :param _force_change: Boolean flag telling if changing the set setting should be forced. Mainly for debugging \
                          and testing purposes. Defaults to False
    :type _force_change: bool, optional

    :raises AssertationError: Raised if invalid type of argument passed

    :return: Void
    :rtype: None
    """
    global _skip_array_checks

    if _skip_array_checks is None:
        if not isinstance(skip, bool):
            _logger.error(f"Invalid argument type {type(skip)} passed to function skip_array_checks. (bool required)")
            raise AssertionError(f"Invalid argument type {type(skip)} passed to function skip_array_checks. (bool required)")
        _skip_array_checks = skip

    elif _force_change:
        if not isinstance(skip, bool):
            _logger.error(f"Invalid argument type {type(skip)} passed to function skip_array_checks. (bool required)")
            raise AssertionError(f"Invalid argument type {type(skip)} passed to function skip_array_checks. (bool required)")
        
        _logger.warning("Changing the settings for the type_check module during program execution not recommended!")
        _skip_array_checks = skip
    
    return _skip_array_checks


def validate(castable: bool = False) -> None:
    """Decorator that validates that the type hints are satisfied. The functions to which this is 
    applied should have a type hint for each parameter aswell as the return type. Depending on the
    value of kwarg 'castable' the type checks are either required to be exact, or it is enough
    that the passed value can be cast to the proper type. Note that the decorator does not do the
    casting and that should be handled properly in the function itself

    :param castable: Boolean flag telling whether to check for exact types of castability. Defaults to False
    :type castable: bool, optional

    :raises AssertationError: Raised if type hints are not satisfied

    :return: Void
    :rtype: None
    """
    if not isinstance(castable, bool):
        _logger.error(f"Invalid argument type {type(castable)} passed to function validate. (bool required)")
        raise AssertionError(f"Invalid argument type {type(castable)} passed to function validate. (bool required)")

    def validate_function(func: callable) -> None:
        
        if skip_validations():
            def inner(*args, **kwargs):
                return func(*args, **kwargs)
            
            return inner

        def inner(*args, **kwargs):
            if not _min_python_satisfied():
                _logger.error("Python version 3.9 or later is required for proper type checking!\
                               If upgrading Python is not an option, the type checks can be ignored by calling 'skip_validations' with kwarg 'skip' set to True.")
                raise AssertionError("Python version 3.9 or later is required for proper type checking!\
                                      If upgrading Python is not an option, the type checks can be ignored by calling 'skip_validations' with kwarg 'skip' set to True.")

            type_hints = get_type_hints(func)

            if len(type_hints) < len(args) + len(kwargs) + 1:
                _logger.error(f"There needs to be a type hint specified for each arg, kwarg and the return value in function {func.__name__}!")
                raise AssertionError(f"There needs to be a type hint specified for each arg, kwarg and the return value in function {func.__name__}!")

            arg_type_hints = list(type_hints.items())[:len(args)]

            for arg, tup in zip(args, arg_type_hints):
                param, type_hint = tup[0], tup[1]

                if not _type_check(arg, type_hint, castable=castable):
                    _logger.error(f"Value {arg} is of improper type for arg {param} in function {func.__name__}! ({type(arg)} != {type_hint})")
                    raise AssertionError(f"Value {arg} is of improper type for arg {param} in function {func.__name__}! ({type(arg)} != {type_hint})")
                
            for key, value in kwargs.items():
                try:
                    type_hint = type_hints[key]
                except KeyError:
                    _logger.error(f"Invalid kwarg key {key} given in function {func.__name__}!")
                    raise AssertionError(f"Invalid kwarg key {key} given in function {func.__name__}!")
                
                if not _type_check(value, type_hint, castable=castable):
                    _logger.error(f"Value {value} is of improper type for kwarg {key} in function {func.__name__}! ({type(value)} != {type_hint})")
                    raise AssertionError(f"Value {value} is of improper type for kwarg {key} in function {func.__name__}! ({type(value)} != {type_hint})")

            ret = func(*args, **kwargs)

            try:
                type_hint = type_hints["return"]
            except KeyError:
                _logger.error(f"The return type is not specified in function {func.__name__}!")
                raise AssertionError(f"The return type is not specified in function {func.__name__}!")
            
            if not _type_check(ret, type_hint, castable=castable):
                _logger.error(f"Return value {ret} is of improper type in function {func.__name__}! ({type(ret)} != {type_hint})")
                raise AssertionError(f"Return value {ret} is of improper type in function {func.__name__}! ({type(ret)} != {type_hint})")

            return ret

        return inner
    
    return validate_function


__all__ = ["skip_validations", "skip_array_checks", "validate"]
