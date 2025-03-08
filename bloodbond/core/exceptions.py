"""
Custom exceptions for the Blood Bond application.

This module defines a hierarchy of exception classes for different error scenarios
in the Blood Bond application, providing more specific error handling and reporting.
"""

class BloodBondError(Exception):
    """Base exception class for all Blood Bond application errors.
    
    All custom exceptions in the application should inherit from this class
    to allow for unified error handling.
    """
    pass


# Data-related exceptions
class DataError(BloodBondError):
    """Base exception for data-related errors.
    
    Used for errors related to data loading, parsing, and validation.
    """
    pass


class FileNotFoundError(DataError):
    """Raised when a required file cannot be found.
    
    This exception should be used when the application cannot locate a
    necessary data file, configuration file, or resource.
    """
    pass


class MalformedDataError(DataError):
    """Raised when data has an invalid structure or format.
    
    This exception should be used when data files (such as JSON) do not 
    conform to the expected structure or have syntax errors.
    """
    pass


class InvalidDataError(DataError):
    """Raised when data values are invalid, despite having correct structure.
    
    This exception should be used when data passes structural validation
    but contains values that are out of range, logically inconsistent, or
    otherwise inappropriate for the application's use.
    """
    pass


# Spell creation exceptions
class SpellError(BloodBondError):
    """Base exception for spell creation and manipulation errors.
    
    Used for errors related to spell creation, validation, and usage.
    """
    pass


class InvalidParameterError(SpellError):
    """Raised when a spell parameter has an invalid value.
    
    This exception should be used when a spell parameter (like level, effect, 
    or element) has a value that doesn't match allowed values or doesn't 
    exist in the reference data.
    """
    pass


class IncompatibleElementsError(SpellError):
    """Raised when trying to combine incompatible spell elements.
    
    This exception should be used when attempting to create a spell with
    an element combination that is not allowed by the game rules.
    """
    pass


class SpellLimitError(SpellError):
    """Raised when exceeding allowed limits for spells.
    
    This exception should be used when creating too many spells, exceeding
    power levels, or otherwise violating spell-related constraints.
    """
    pass


class SpellValidationError(SpellError):
    """Raised when a spell fails validation checks.
    
    This exception should be used when a spell object doesn't meet the 
    requirements for being a valid spell, but the exact reason doesn't 
    fit into more specific exception types.
    """
    pass


# User interface exceptions
class UIError(BloodBondError):
    """Base exception for user interface errors.
    
    Used for errors related to the user interface, such as invalid input
    or configuration.
    """
    pass


class InputValidationError(UIError):
    """Raised when user input fails validation.
    
    This exception should be used when the user provides input that doesn't
    meet validation requirements (e.g., empty fields, invalid formats).
    """
    pass


class ResourceLoadError(UIError):
    """Raised when UI resources cannot be loaded.
    
    This exception should be used when the application fails to load resources
    needed for the UI, such as fonts, images, or theme elements.
    """
    pass


class UIConfigurationError(UIError):
    """Raised when the UI is improperly configured.
    
    This exception should be used when there's an issue with the configuration
    of UI elements, such as missing required components or invalid layout.
    """
    pass

