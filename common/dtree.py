"""This class is inherited from dictionary and represents a column in the table of the evil DICOM
"""
from error import (BranchNotDeclared,LengthNotEqual)
class DTree(list):
    __keys__= ('name',)
    def __init__(self,*args,**kwargs):
        self.__metainfo__={}
        self.set_metainfo(self,*args,**kwargs)
        for __key__ in self.__keys__:
            if __key__ not in self.__metainfo__:
                self.__metainfo__[__key__]=None
    def get_metainfo(self):
        return self.__metainfo__
    def set_metainfo(self,*args,**kwargs):
        for key, value in kwargs.items():
            for __key__ in self.__keys__:
                if key==__key__:
                    self.__metainfo__[__key__]=value
    def add_branch(self,branchname):
        if isinstance(branchname,str):
            _is_new_=True
            for i in self:
                if branchname==i.get_metainfo()['name']:
                    _is_new_=False
            if _is_new_:
                if not self._is_equal_length_():
                    raise LengthNotEqual()
                self.append(DBranch(name=branchname))
                if len(self)>0:
                    for i in range(len(self[0])):
                        self.add_leaf(branch=branchname,value=None)
        else:
            raise TypeError('The passed object is not of type str')
    def get_branch(self,branchname):
        result=None
        for i in self:
            print i.get_metainfo()
            if branchname==i.get_metainfo()['name']:
                result=i
        return result

    def del_branch(self,branchname):
        for i in self:
            if branchname==i.get_metainfo()['name']:
                del self[self.index(i)]
    def _is_equal_length_(self):
        result=True
        if len(self)>0:
            _first_length_=len(self[0])
            for i in self:
                if _first_length_!=len(i):
                    result=False
        return result
    """For the convenience of the caller, this method takes in "branch=<branchname,value=<new value>"
    and add the <new value> to the end of the appropriate branch. This function also makes sure that
    all branches are of the equal length. Therefore you should call this function instead of appending
    to the branch directly
    """
    def add_leaf(self,*args,**kwargs):
        branchname=None
        new_val=None
        for key,value in kwargs.items():
            if key=='branch':
                for i in self:
                    if value==i.get_metainfo()['name']:
                        branchname=value
            if key=='value':
                new_val=value
        if branchname==None:
            raise BranchNotDeclared()
        if not self._is_equal_length_(self):
            raise LengthNotEqual()
        self.get_branch(branchname).append(new_val)
        new_index=self.get_branch(branchname).index(new_val)
        for i in self:
            if len(i)<(new_index+1):
                i.append(None)
    def _get_index_(self,*args,*kwargs):

class DBranch(list):
    __keys__=('name',)
    def __init__(self,*args,**kwargs):
        self.__metainfo__={}
        self.set_metainfo(self,*args,**kwargs)
        for __key__ in self.__keys__:
            if __key__ not in self.__metainfo__:
                self.__metainfo__[__key__]=None
    def get_metainfo(self):
        return self.__metainfo__
    def set_metainfo(self,*args,**kwargs):
        for key, value in kwargs.items():
            for __key__ in self.__keys__:
                if key==__key__:
                    self.__metainfo__[__key__]=value
