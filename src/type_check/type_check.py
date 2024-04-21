"""
Module defining decorators for static type checking.

The errors raised by these decorators will not be logged as they should merely
be guards from bad programming and should never be raised during program execution.

Note that type subscription requires Python 3.9 or later!
"""
from __future__ import annotations
from typing import get_type_hints, _GenericAlias
import sys


# Global variable holding the info on whether the validations should be skipped
# Accessible by the skip_validations function
_skip_validations = None


def _min_python_satisfied() -> bool:
    """Function that checks that the minimum Python version is satisfied.
    The minimum version is Python 3.9, which first implemented type subscription.

    :return: True if minimum version is satisfied, False otherwise
    :rtype: bool
    """
    return sys.version_info >= (3, 9)


def _type_check(value: any, type_hint: any) -> bool:
    """Function for checking that the type is satisfied

    :param value: The value to be checked
    :type value: any
    :param type_hint: The type that was hinted
    :type type_hint: any

    :return: True if value matches the type hint, False otherwise
    :rtype: bool
    """
    # Check if type is callable
    if type_hint == callable:
        return callable(value)
    
    # Check if type is a typing.Union[...] and the value is any of the given types
    if isinstance(type_hint, _GenericAlias):
        return isinstance(value, type_hint.__args__)
    
    return isinstance(value, type_hint)


def _castable_check(value: any, type_hint: any) -> bool:
    """Function for checking that the type is satisfied, or value can be cast to it.
    TODO: Implement once a proper casting system is figured out

    :param value: The value to be checked
    :type value: any
    :param type_hint: The type that was hinted
    :type type_hint: any

    :return: True if value matches the type hint or is castable, False otherwise
    :rtype: bool
    """
    raise NotImplementedError


def skip_validations(skip: bool = False) -> None:
    """Function that determines if validations should be skipped. If the validations are
    skipped some overhead might be reduced, but with the cost of possible undefined behavior.

    :param skip: Boolean telling if the validation skips should be performed. Defaults to False
    :type skip: bool, optional

    :raises AssertationError: Raised if invalid type of argument passed

    :return: Void
    :rtype: None
    """
    global _skip_validations
    if _skip_validations is None:
        assert isinstance(skip, bool), f"Invalid argument type {type(skip)} passed to function skip_validations. (bool required)"
        _skip_validations = skip
    
    return _skip_validations


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
    assert isinstance(castable, bool), f"Invalid argument type {type(castable)} passed to function validate. (bool required)"

    if castable:
        check_func = _castable_check
    else:
        check_func = _type_check

    def validate_function(func: callable) -> None:
        
        if skip_validations():
            def inner(*args, **kwargs):
                return func(args, kwargs)
            
            return inner

        def inner(*args, **kwargs):
            if not _min_python_satisfied():
                raise AssertionError("Python version 3.9 or later is required for proper type checking!")

            type_hints = get_type_hints(func)

            assert len(type_hints) >= len(args) + len(kwargs) + 1, f"There needs to be a type hint specified for each arg, kwarg and the return value in function {func.__name__}!"

            arg_type_hints = list(type_hints.items())[:len(args)]

            for arg, tup in zip(args, arg_type_hints):
                param, type_hint = tup[0], tup[1]

                assert check_func(arg, type_hint), f"Value {arg} is of improper type for arg {param} in function {func.__name__}! ({type(arg)} != {type_hint})"
                
            for key, value in kwargs.items():
                try:
                    type_hint = type_hints[key]
                except KeyError:
                    raise AssertionError(f"Invalid kwarg key {key} given in function {func.__name__}!")
                
                assert check_func(value, type_hint), f"Value {value} is of improper type for kwarg {key} in function {func.__name__}! ({type(value)} != {type_hint})"

            ret = func(args, kwargs)

            try:
                type_hint = type_hints["return"]
            except KeyError:
                raise AssertionError(f"The return type is not specified in function {func.__name__}!")
            
            assert check_func(ret, type_hint), f"Return value {ret} is of improper type in function {func.__name__}! ({type(ret)} != {type_hint})"

            return ret

        return inner
    
    return validate_function


__all__ = ["skip_validations", "validate"]
