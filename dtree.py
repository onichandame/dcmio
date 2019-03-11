"""This class is inherited from dictionary and represents a column in the table of the evil DICOM
"""
from error import (BranchNotDeclared,LengthNotEqual,DuplicatedBranchError,BranchNotEqual,ValueNotUnique)
class DTree(list):
    __keys__= ('name','level','index')
    _dicom_branches_=('tag','VR','VM','name','value')
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
        if 'value' in _tree_._get_branches_():
            for i in _tree_.get_branch('value'):
                if len(str(i))>60:
                    _tree_.get_branch('value')[_tree_.get_branch('value').index(i)]=len(str(i))
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
            result=result+'No. of attributes: '+str(_tree_.get_length())+'\r\n'
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
            for i in range(_tree_.get_length()):
                result=result+'|'
                for key,value in length.items():
                    _value_=str(_tree_.get_branch(key)[i])
                    result=result+_value_+' '*(value-len(_value_))+'|'
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
            index=-1
            for i in self.get_branch(key):
                if isinstance(value,list):
                    if i in value:
                        index=self.get_branch(key).index(i,index+1)
                        result.append(index)
                else:
                    if i==value:
                        index=self.get_branch(key).index(i,index+1)
                        result.append(index)
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
    def _get_branches_(self):
        result=[]
        _raw_branch_=None
        for i in self:
            result.append(i.get_metainfo()['name'])
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
        if args:
            if len(args)==1:
                _field_=args[0]
            else:
                raise NotImplementedError('The expected args must be unique')
        else:
            _field_='value'
        if isinstance(_field_,int):
            return self.get_branch('value')[_field_]
        elif isinstance(_field_,str):
            if _field_ not in self._get_branches_():
                raise TypeError('The received branch name is not present in the tree')
            searched=self.get_attributes(*args,**kwargs)
            if searched.get_length()==1:
                result=searched.get_branch(_field_)[0]
            elif searched.get_length()==0:
                return None
            else:
                raise ValueNotUnique()
            return result
        else:
            raise TypeError('The expected type is str or int but received {}'.format(type(_field_)))

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
    def set_value(self,newval,*args,**kwargs):
        if self._is_duplicated_branch_():
            raise DuplicatedBranchError()
        if not self._is_equal_length_():
            raise LengthNotEqual()
        if kwargs:
            _indices_=self._get_index_(*args,**kwargs)
            if len(_indices_)!=1:
                raise TypeError('The condition specified has no matched result')
            for i in _indices_:
                _indices_=i
                break
            if len(args)!=1:
                raise TypeError('The specified branch must be unique')
        else:
            if len(args)!=2:
                raise TypeError()
            if not isinstance(args[1],int):
                raise TypeError()
            _indices_=args[1]
        if args[0] not in self._get_branches_():
            raise BranchNotDeclared('The specified branch is not present')
        self.get_branch(args[0])[_indices_]=newval
    """From this line down, methods are only desighed for use in DICOM format: 5 branches(tag,VR,VM,name,value)
    """
    def _value_to_bin_(self,index,**kwargs):
        _param_={}
        _param_['littleEndian']=True
        from dcmread import default_encoding
        _param_['encoding']=default_encoding
        for key,value in kwargs.items():
            if key in _param_.keys():
                _param_[key]=value
        VR=self.get_branch('VR')[index]
        value=self.get_branch('value')[index]
        from dcmread import text_VRs
        if VR in text_VRs:
            if len(value)%2!=0:
                value=value+'\0'
            result=value.encode(_param_['encode'],'strict')
        else:
            if len(value)%2!=0:
                value=str(value)+' '
            result=value.encode(_param_['encode'],'strict')
        return result
    def _attribute_to_bin_(self,index,*args,**kwargs):
        for i in self._dicom_branches_:
            if i not in self._get_branches_():
                raise TypeError('The DTree instance does not hold the structure of DICOM')
        if self._is_duplicated_branch_():
            raise DuplicatedBranchError()
        if not self._is_equal_length_():
            raise LengthNotEqual()
        _param_={}
        _param_['littleEndian']=True
        _param_['implicity']=False
        from dcmread import default_encoding
        _param_['encoding']=default_encoding
        for key,value in kwargs.items():
            if key in _param_.keys():
                _param_[key]=value
        if _param_['littleEndian']:
            _end_char_='<'
        else:
            _end_char_='>'
        _struct_param_=_end_char_+'HH'
        _struct_=[]
        _tag_=self.get_branch('tag')[index]
        _struct_.append(_tag_>>16,_tag_&0xffff)
        _bin_value_=_value_to_bin_(index)
        _bin_leng_=len(_bin_value_)
        if _param_['implicity']:
            _struct_VR_leng_='L'
            _struct_.append(_bin_leng_)
        else:
            _struct_VR_leng_='2sH'
            _struct_.append(self.get_branch('VR')[index])
            _struct_.append(_bin_leng_)
        _struct_param_=_struct_param_+_struct_VR_leng_
        from struct import Struct
        _meta_struct_pack=Struct(_struct_param_).pack
        if index<self.get_length():
            result=_meta_struct_pack(_struct_)
        else:
            raise IndexError('The passed index has exceeded the allowed range')
        return result
    """This methods is designed to write DTree instances to file(s)
    input: *outpath
           *filename
           max_byte
           littleEndian
           encoding
    """
    def _header_to_bin_(self):
        for i in self._dicom_branches_:
            if i not in self._get_branches_():
                raise TypeError('The DTree instance does not hold the structure of DICOM')
        if self._is_duplicated_branch_():
            raise DuplicatedBranchError()
        if not self._is_equal_length_():
            raise LengthNotEqual()
        _tag_=self.get_branch('tag')
        _header_indices_=[]
        for i in _tag_:
            if not isinstance(i,int):
                raise TypeError('The expected type is int but received {}'.format(type(i)))
            if i<<16 == 0x0002:
                _header_indices_.append(_tag_.index(i))
        if not _header_indices_:
            raise NotImplementedError('Currently dcmio is not capable of dealing with files without DICOM header')
        result=b''
        for i in _header_indices_:
            if self.get_branch('tag')[i]==0x00020000:
                continue
            result=result+_attribute_to_bin_(i)
        header_len=len(result)
        header_len_value=
        result=Struct('<HH2sH').pack(0x0002,0x0000,'UL',)
        return result
    def write(self,*args,**kwargs):
        _neccessary_input_=('outpath','filename','max_byte')
        _all_input_=_neccessary_input_+('max_byte','littleEndian','encoding')
        config={}
        for key,value in kwargs.items():
            if key in _all_input_:
                config[key]=value
        for i in _neccessary_input_:
            if i not in config.keys():
                raise KeyError('An argument {} is missing in the passed arguments'.format(i))
        for i in _all_input_:
            if i not in config.keys():
                if i=='max_byte':
                    config[i]=10000000
                elif i=='littleEndian':
                    config[i]=True
                elif i=='encoding':
                    from dcmread import default_encoding
                    config[i]=default_encoding
        _header_bin_=self._header_to_bin_()
        _data_bin_=self._data_to_bin_()
        _bin_=_header_to_bin_+_data_to_bin_
        with open(outpath+filename,'wb') as filewriter:
            filewriter.write(_header_to_bin_+_data_to_bin_)


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
