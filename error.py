class InvalidDicomError(Exception):
    """This class handles the error when the input file is not a valid dicom file
    """
    def __init__(self, *args):
        if not args:
            args=('The file read is not a valid DICOM file', )
        Exception.__init__(self,*args)

class InvalidEncodingError(Exception):
    """Exception that is raised when the encoding scheme of the file
    is not in the standard DICOM scheme. Could correct some typo
    to reduce the chance of raising this exception
    """
    def __init__(self,*args):
        if not args:
            args = ('The encoding scheme could not be understood.',)
        Exception.__init__(self,*args)

class InvalidSQError(Exception):
    """When the first attribute in a sequence is not the starting attribute, This
    error is raised
    """
    def __init__(self,*args):
        if not args:
            args=('The sequence is invalid',)
        Exception.__init__(self,*args)

class InvalidPixelDimension(Exception):
    def __init__(self,*args):
        if not args:
            args=('The dimension of the pixels is invalid',)
        Exception.__init__(self,*args)

class EmptyListError(Exception):
    def __init__(self, *args):
        if not args:
            args=('The list is empty', )
        Exception.__init__(self,*args)

class InputFileError(Exception):
    def __init__(self, *args):
        if not args:
            args=('An error occured when reading the input file', )
        Exception.__init__(self,*args)

class EmptySequenceError(Exception):
    def __init__(self, *args):
        if not args:
            args=('An empty sequence is read. need further development', )
        Exception.__init__(self,*args)

class BranchNotDeclared(Exception):
    def __init__(self, *args):
        if not args:
            args=('The branch specified is not present in the DTree', )
        Exception.__init__(self,*args)

class LengthNotEqual(Exception):
    def __init__(self, *args):
        if not args:
            args=('The length of branches are not equal', )
        Exception.__init__(self,*args)

class DuplicatedBranchError(Exception):
    def __init__(self, *args):
        if not args:
            args=('There are duplicated branches with the same name', )
        Exception.__init__(self,*args)

class BranchNotEqual(Exception):
    def __init__(self, *args):
        if not args:
            args=('The branches selected for merge have different branches', )
        Exception.__init__(self,*args)

class ValueNotUnique(Exception):
    def __init__(self, *args):
        if not args:
            args=('The searched result has more than 1 entry', )
        Exception.__init__(self,*args)

class ItemNotFound(Exception):
    def __init__(self, *args):
        if not args:
            args=('expect an item but not found', )
        Exception.__init__(self,*args)

class VRNotSpecified(Exception):
    def __init__(self, *args):
        if not args:
            args=('Trying to read an attribute with no VR specified. Check the code', )
        Exception.__init__(self,*args)

