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

