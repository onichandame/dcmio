"""This class is inherited from dictionary and represents a column in the table of the evil DICOM
"""
from error import (BranchNotDeclared,LengthNotEqual,DuplicatedBranchError,BranchNotEqual,ValueNotUnique)
class DTree(list):
    __keys__= ('name','level','index')
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
    def _is_duplicated_branch_(self):
        result=False
        if len(self)>0:
            names=[]
            for i in self:
                names.append(i.get_metainfo()['name'])
            if len(names)!=len(set(names)):
                result=True
        return result
    def _num_len_(self,num):
        #To do: add support for floating point numbers
        #Currently it only supports integer
        from math import log10
        if num>0:
            result=int(log10(num))+1
        elif num==0:
            result=1
        else:
            result=int(log10(-n))+2
        return result
    def __str__(self,_max_entries_=-1):#To do: add support for length specification
        if self._is_duplicated_branch_():
            raise DuplicatedBranchError()
        if not self._is_equal_length_():
            raise LengthNotEqual()
        if _max_entries_==-1 or _max_entries_>len(self[0]):
            _tree_=self
        else:
            from copy import deepcopy
            _tree_=deepcopy(self)
            for i in _tree_:
                _tree_[_tree_.index(i)]=i[:_max_entries_]
            if not _tree_._is_equal_length_():
                raise LengthNotEqual()
        length={}
        for i in _tree_:
            length[i.get_metainfo()['name']]=len(i.get_metainfo()['name'])
            for j in i:
                if len(str(j))>length[i.get_metainfo()['name']]:
                    length[i.get_metainfo()['name']]=len(str(j))
        if not length:
            length={'':0}
        result=''
        for key,value in _tree_.get_metainfo().items():
            result=result+key+': '+str(value)+'\r\n'
        if not _tree_:
            result=result+'No. of attributes: '+str(0)+'\r\n'
        else:
            result=result+'No. of attributes: '+str(len(_tree_[0]))+'\r\n'
        _total_length_=1
        for key,value in length.items():
            _total_length_=_total_length_+value+1
        result=result+'*'*_total_length_+'\r\n'
        result=result+'*'*_total_length_+'\r\n'
        result=result+'+'
        for key,value in length.items():
            result=result+'-'*value+'+'
        result=result+'\r\n|'
        for key,value in length.items():
            result=result+key+' '*(value-len(key))+'|'
        result=result+'\r\n+'
        for key,value in length.items():
            result=result+'-'*value+'+'
        result=result+'\r\n+'
        for key,value in length.items():
            result=result+'-'*value+'+'
        result=result+'\r\n'
        if _tree_:
            for i in range(len(_tree_[0])):
                result=result+'|'
                for key,value in length.items():
                    result=result+str(_tree_.get_branch(key)[i])+' '*(value-len(str(_tree_.get_branch(key)[i])))+'|'
                result=result+'\r\n+'
                for key,value in length.items():
                    result=result+'-'*value+'+'
                result=result+'\r\n'
        return result
    """For the convenience of the caller, this method takes in "branch=<branchname,value=<new value>"
    and add the <new value> to the end of the appropriate branch. You should call this function instead
    of appending to the branch directly
    """
    def add_leaf(self,*args,**kwargs):
        pair=self._get_pair_(self,*args,**kwargs)
        self.get_branch(pair['name']).append(pair['value'])
    def _get_pair_(self,*args,**kwargs):
        result={}
        result['name']=None
        result['value']=None
        for key,value in kwargs.items():
            if key=='branch':
                for i in self:
                    if value==i.get_metainfo()['name']:
                        result['name']=value
            if key=='value':
                result['value']=value
        if result['name']==None:
            raise BranchNotDeclared()
        return result
    def _get_index_(self,*args,**kwargs):
        if self._is_duplicated_branch_():
            raise DuplicatedBranchError()
        _conditions_=self._get_condition_(*args,**kwargs)
        result=[]
        for key, value in _conditions_.items():
            for i in self.get_branch(key):
                if isinstance(value,list):
                    if i in value:
                        result.append(self.get_branch(key).index(i))
                else:
                    if i==value:
                        result.append(self.get_branch(key).index(i))
        result=set(result)
        return result
    def _check_branch_(self,branches):
        result=branches
        _name_=[]
        for i in self:
            _name_.append(i.get_metainfo()['name'])
        for i in result:
            if i not in _name_:
                del result[result.index(i)]
        return result
    def _get_condition_(self,*args,**kwargs):
        #_operators_=('()',('!=','=='),'!','&&','||') To do: add support for condition in string
        result={}
        for key,value in kwargs.items():
            if key not in result:
                result[key]=value
        _checked_branches_=self._check_branch_(list(result.keys()))
        for key,value in result.items():
            if key not in _checked_branches_:
                del result[key]
        if len(result)==0:
            raise BranchNotDeclared('you have not specified at least 1 branch. Use syntax branch=\'branch1:branch2\'')
        for key,value in result.items():
            if isinstance(value,str):
                if ":" in value:
                    result[key]=value.split(":")
        return result
    def _get_branches_(self,*args,**kwargs):
        result=[]
        _raw_branch_=None
        for key,value in kwargs.items():
            if key=='branch':
                _raw_branch_=value
        if not _raw_branch_:
            raise BranchNotDeclared('you have not specified at least 1 branch. Use syntax branch=\'branch1:branch2\'')
        result=_raw_branch_.split(":")
        result=self._check_branch_(result)
        if len(result)==0:
            raise BranchNotDeclared()
        return result
    def get_attributes(self,*args,**kwargs):
        _indices_=self._get_index_(*args,**kwargs)
        result=DTree(name='result')
        _branches_=[]
        for i in self:
            result.add_branch(i.get_metainfo()['name'])
            _branches_.append(i.get_metainfo()['name'])
        for i in _indices_:
            for j in _branches_:
                result.add_leaf(branch=j,value=self.get_branch(j)[i])
        if not result._is_equal_length_():
            raise LengthNotEqual()
        return result
    def del_attributes(self,*args,**kwargs):
        _indices_=self._get_index_(*args,**kwargs)
        for i in self:
            for j in _indices_:
                del i[j]
    def get_length(self):
        if not self._is_equal_length_():
            raise LengthNotEqual()
        if not self:
            return -1
        elif not self[0]:
            return 0
        else:
            return len(self[0])
    def get_value(self,*args,**kwargs):
        searched=self.get_attributes(*args,**kwargs)
        if searched.get_length()==1:
            result=searched.get_branch('value')[0]
        elif searched.get_length()==0:
            return None
        else:
            raise ValueNotUnique()
        return result

    """This function merges a tree into self. usage: tree1.merge(tree2), result: entries of tree2 are appended
    to the end of tree1 while losing the metainfo of tree2. Currently only trees with the same set of branches can be merged.
    """
    def merge(self,tree):
        if not isinstance(tree,DTree):
            raise TypeError('The required argument is of the type DTree.')
        if not self._is_equal_length_() or not tree._is_equal_length_():
            raise LengthNotEqual()
        if self._is_duplicated_branch_() or tree._is_duplicated_branch_():
            raise DuplicatedBranchError()
        _self_branches_=[]
        _tree_branches_=[]
        for i in self:
            _self_branches_.append(i.get_metainfo()['name'])
        for i in tree:
            _tree_branches_.append(i.get_metainfo()['name'])
        if sorted(_self_branches_) != sorted(_tree_branches_):
            raise BranchNotEqual()
        _tree_length_=tree.get_length()
        if _tree_length_<1:
            return
        else:
            for i in range(_tree_length_):
                for j in _self_branches_:
                    self.add_leaf(branch=j,value=tree.get_branch(j)[i])
    def add_attribute(self,attr):
        from dcmread import attribute
        if not isinstance(attr,attribute):
            raise TypeError('The required type is attribute but received {}'.format(type(attr)))
        if self._is_duplicated_branch_():
            raise DuplicatedBranchError()
        if not self._is_equal_length_():
            raise LengthNotEqual()
        _names_=[]
        for i in self:
            _names_.append(i.get_metainfo()['name'])
        _names_=tuple(_names_)
        if _names_ != attr._fields:
            raise BranchNotEqual('The tree selected has different branches than the attribute passed')
        for i in _names_:
            self.add_leaf(branch=i,value=getattr(attr,i))

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
