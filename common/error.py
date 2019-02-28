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
