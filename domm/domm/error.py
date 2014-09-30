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

class DuplicateParamError(DommError):
    """
    Error raised when there are two or more parameters have the same name
    """
    def __init__(self, value):
        super(DuplicateParamError, self).__init__("")
        self.message = ' Operation parameter with value "%s" already declared! ' % (value)

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

class ConstraintDoesntApplyError(DommError):
    """
    Error raised when constraints fail the check
    """
    def __init__(self, name, field):
        super(ConstraintDoesntApplyError, self).__init__("")
        self.message = 'Constraint <"%s"> does not apply to field <"%s"> ' % (name, field)

class WrongConstraintError(DommError):
    """
    Error raised when constraints fail the check
    """
    def __init__(self, name, param):
        super(WrongConstraintError, self).__init__("")
        self.message = 'Constraint <"%s"> does not allow a parameter <"%s"> there ' % (name, param)

class WrongConstraintAtPosError(DommError):
    """
    Error raised when constraints fail the check
    """
    def __init__(self, name, param, pos):
        super(WrongConstraintAtPosError, self).__init__("")
        self.message = 'Constraint <"%s"> does not allow a parameter <"%s"> at position (pos:%s)' \
                        % (name, param, pos +1)

class NoParameterError(DommError):
    """
    Error raised when constraints fail the check
    """
    def __init__(self, name):
        super(NoParameterError, self).__init__("")
        self.message = 'Constraint <"%s"> has no parameters ' % (name)

class WrongNumberOfParameterError(DommError):
    """
    Error raised when constraints fail the check
    """
    def __init__(self, name, expected, found):
        super(WrongNumberOfParameterError, self).__init__("")
        self.message = 'Constraint <"%s"> at (number of params: %s) not %s ' % (name, expected, found)

class KeywordError(DommError):
    """
    Error raised when name matches keyword
    """
    def __init__(self, name):
        super(KeywordError, self).__init__("")
        self.message = "Can't use %s as identifier. That value is a reserved word." % name

class ContainmentError(DommError):
    """
    Error raised when element is used in contaiment twice.
    """
    def __init__(self, name):
        super(ContainmentError, self).__init__("")
        self.message = "The type %s is already in containment." % name
