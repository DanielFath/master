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
