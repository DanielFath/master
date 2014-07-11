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
    Error when id was already declared
    """
    def __init__(self, name):
        super(IdExistsError, self).__init__("")
        self.message = ' Id <"%s"> already taken ' % (name)

class TypeExistsError(DommError):
    """
    Error when dataType with same name was already declared
    """
    def __init__(self, name):
        super(TypeExistsError, self).__init__("")
        self.message = ' dataType <"%s"> already declared ' % (name)

class DuplicateLiteralError(DommError):
    """
    Error when there are two or more literals in enum with same name
    """
    def __init__(self, name):
        super(DuplicateLiteralError, self).__init__("")
        self.message = ' Literal with name "%s" already exist! ' % (name)

class ElipsisMustBeLast(DommError):
    """
    Error when `...` isn't last element in syntax
    """
    def __init__(self, name):
        super(ElipsisMustBeLast, self).__init__("")
        self.message = ' The ... must be last element. ' % (name)

class DuplicateTypeError(object):
    """docstring for DuplicateTypeError"""
    def __init__(self, name):
        super(DuplicateTypeError, self).__init__()
        self.message = 'A type with name "%s" already exists!' % (name)
