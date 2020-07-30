#!/usr/bin/env python3
# coding=utf-8

import sys
from functools import wraps
from io import StringIO

from unittest.mock import patch


def redirect_stdout(func):
    """temporarily redirect stdout to new output stream"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        original_stdout = sys.stdout
        out = StringIO()
        try:
            sys.stdout = out
            return func(out, *args, **kwargs)
        finally:
            sys.stdout = original_stdout
    return wrapper


def use_user_prefs(user_prefs):
    """temporarily use the given values for user preferences"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with patch('yvs.core.get_user_prefs', return_value=user_prefs):
                return func(*args, **kwargs)
        return wrapper
    return decorator
