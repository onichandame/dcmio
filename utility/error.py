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
