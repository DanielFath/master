class DommError(Exception):
    """
    Base class for DOMM Parser errors.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)

class IdExistsError(DommError):
    """
    Error raised when id was already declared
    """
    def __init__(self, name):
        super(IdExistsError, self).__init__("")
        self.message = ' Id <"%s"> already taken ' % (name)

class TypeExistsError(DommError):
    """
    Error raised when dataType with same name was already declared
    """
    def __init__(self, name):
        super(TypeExistsError, self).__init__("")
        self.message = ' dataType <"%s"> already declared ' % (name)

class DuplicateLiteralError(DommError):
    """
    Error raised when there are two or more literals in enum with same name
    """
    def __init__(self, name):
        super(DuplicateLiteralError, self).__init__("")
        self.message = ' Literal with name "%s" already exist! ' % (name)

class ElipsisMustBeLast(DommError):
    """
    Error raised when `...` isn't last element in syntax
    """
    def __init__(self, name):
        super(ElipsisMustBeLast, self).__init__("")
        self.message = ' The ... must be last element. ' % (name)

class DuplicateTypeError(object):
    def __init__(self, name):
        super(DuplicateTypeError, self).__init__()
        self.message = 'A type with name "%s" already exists!' % (name)

class ExceptionExistsError(DommError):
    """
    Error raised when dataType with same name was already declared
    """
    def __init__(self, name):
        super(ExceptionExistsError, self).__init__("")
        self.message = ' exception with name <"%s"> already declared ' % (name)

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

