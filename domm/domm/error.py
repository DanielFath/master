##############################################################################
# Name: error.py
# Purpose: Errors used in DOMMLite parser
# Author: Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# Copyright: (c) 2014 Daniel Fath <daniel DOT fath7 AT gmail DOT com>
# License: MIT License
##############################################################################
class DommError(Exception):
    """
    Base class for DOMM Parser errors.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)

class DuplicateLiteralError(DommError):
    """
    Error raised when there are two or more literals in enum with same name
    """
    def __init__(self, value):
        super(DuplicateLiteralError, self).__init__("")
        self.message = ' Literal with value "%s" already exist! ' % (value)

class ElipsisMustBeLast(DommError):
    """
    Error raised when `...` isn't last element in syntax
    """
    def __init__(self, name):
        super(ElipsisMustBeLast, self).__init__("")
        self.message = ' The ... must be last element. ' % (name)

class DuplicateTypeError(DommError):
    def __init__(self, type_of, name):
        super(DuplicateTypeError, self).__init__("")
        self.message = 'A %s with name "%s" already exists!' % (type_of, name)

class DuplicateExceptionError(DommError):
    def __init__(self, op, excp):
        super(DuplicateExceptionError, self).__init__("")
        self.message = 'The operation `%s` already throws exception(%s) already exists!' % (op, excp)

class ExceptionExistsError(DommError):
    """
    Error raised when dataType with same name was already declared
    """
    def __init__(self, name):
        super(ExceptionExistsError, self).__init__("")
        self.message = ' exception with name <"%s"> already declared ' % (name)

class DuplicateConstrError(DommError):
    """
    Error raised when classifier has duplicate constraintss
    """
    def __init__(self, name):
        super(DuplicateConstrError, self).__init__("")
        self.message = ' Constraint with name <"%s"> already applied ' % (name)

class DuplicateDependsError(DommError):
    """
    Error raised when classifier has duplicate depency declarations
    """
    def __init__(self, name):
        super(DuplicateDependsError, self).__init__("")
        self.message = ' Depenedcy with name <"%s"> already declared ' % (name)

class DuplicatePropertyError(DommError):
    """
    Error raised when two properties in a field have same name
    """
    def __init__(self, name):
        super(DuplicatePropertyError, self).__init__("")
        self.message = ' Property with name <"%s"> already declared ' % (name)

class DuplicateFeatureError(DommError):
    """
    Error raised when two properties in a field have same name
    """
    def __init__(self, name):
        super(DuplicateFeatureError, self).__init__("")
        self.message = ' Feature with name <"%s"> already exists ' % (name)

class TypeNotFoundError(DommError):
    """
    Error raised when type isn't found isn't specified
    """
    def __init__(self, name):
        super(TypeNotFoundError, self).__init__("")
        self.message = 'Type <"%s"> not found ' % name
