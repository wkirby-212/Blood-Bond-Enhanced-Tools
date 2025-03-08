"""
Utility functions and classes for the Blood Bond Enhanced Tools package.

This subpackage contains helper utilities for string processing, configuration
management, and other general-purpose functionality.
"""

from bloodbond.utils.string_utils import *
from bloodbond.utils.config import Config

# Import all string utility functions
__all__ = ['Config']

# Add any string utility functions to __all__
try:
    from bloodbond.utils.string_utils import __all__ as string_utils_all
    __all__.extend(string_utils_all)
except ImportError:
    # If string_utils doesn't define __all__, we'll just use what we know
    pass

