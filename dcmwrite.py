from dtree import DTree
def _value_to_bin_(tree,index,**kwargs):
    _required_param_=('littleEndian','implicity','encoding')
    for i in _required_param_:
        if i not in kwargs.keys():
            raise NotImplementedError(str(_required_param_)+' are required but received {}'.format(str(kwargs)))
    VR=tree.get_branch('VR')[index]
    value=tree.get_branch('value')[index]
    if tree.get_branch('tag')[index]==0x00020002 or tree.get_branch('tag')[index]==0x00020010:
        from _uid_dict import UID_dictionary
        for key,val in UID_dictionary.items():
            if value in val:
                value = str(key)
    if VR not in converters.keys():
        raise NotImplementedError('VR {} not recognized'.format(VR))
    if isinstance(converters[VR],tuple):
        converter,struct_format=converters[VR]
    else:
        converter=converters[VR]
        struct_format=None
    result=converter(value=value,struct_format=struct_format,**kwargs)
    return result
def _attribute_to_bin_(tree,*args,**kwargs):
    for i in tree._dicom_branches_:
        if i not in tree._get_branches_():
            raise TypeError('the dtree instance does not have the structure of dicom')
    if tree._is_duplicated_branch_():
        from error import DuplicatedBranchError
        raise DuplicatedBranchError()
    if not tree._is_equal_length_():
        from error import LengthNotEqual
        raise LengthNotEqual()
    if args:
        if isinstance(args[0],int):
            index=args[0]
    elif kwargs:
        _index_=tree._get_index_(*args,**kwargs)
        if _index_:
            if len(_index_)==1:
                for i in _index_:
                    index=i
            else:
                raise IndexError('the expected index is unique but received multiple or no matches {}'.format(_index_))
        else:
            raise IndexError('the expected index is unique but received no matches {}'.format(_index_))
    else:
        raise IndexError('the expected index is necessary but received no parameter')
    _required_param_=('littleEndian','implicity','encoding')
    _param_={}
    for i in _required_param_:
        if i in kwargs.keys():
            _param_[i]=kwargs[i]
        else:
            raise NotImplementedError(str(_required_param_)+' are required parameters but received {}'.format(str(kwargs)))
        _end_char_='><'[_param_['littleEndian']]
    _struct_param_=_end_char_+'HH'
    _struct_=[]
    _tag_=tree.get_branch('tag')[index]
    _struct_.extend([_tag_>>16,_tag_&0xffff])
    _bin_value_=_value_to_bin_(tree,index,**kwargs)
    _bin_leng_=len(_bin_value_)
    if _param_['implicity']:
        _struct_vr_leng_='L'
        _struct_param_=_struct_param_+_struct_vr_leng_
        _struct_.append(_bin_leng_)
    else:
        _struct_vr_leng_='2sH'
        from dcmread import default_encoding
        _struct_.append(tree.get_branch('VR')[index].encode(default_encoding))
        from dcmread import extra_length_VRs
        if tree.get_branch('VR')[index] in extra_length_VRs:
            _struct_param_=_struct_param_+_struct_vr_leng_+'L'
            _struct_.extend([0,_bin_leng_])
        else:
            _struct_param_=_struct_param_+_struct_vr_leng_
            _struct_.append(_bin_leng_)
    from struct import Struct
    _meta_struct_pack=Struct(_struct_param_).pack
    if index<tree.get_length():
        result=_meta_struct_pack(*_struct_)+_bin_value_
    else:
        raise IndexError('the passed index has exceeded the allowed range')
    return result
"""this methods is designed to write dtree instances to file(s) input: *outpath
       *filename
       max_byte
       littleEndian
       encoding
"""
def _header_to_bin_(tree):
    for i in tree._dicom_branches_:
        if i not in tree._get_branches_():
            raise TypeError('the dtree instance does not hold the structure of dicom')
    if tree._is_duplicated_branch_():
        from error import DuplicatedBranchError
        raise DuplicatedBranchError()
    if not tree._is_equal_length_():
        from error import LengthNotEqual
        raise LengthNotEqual()
    _tag_=tree.get_branch('tag')
    _header_indices_=[]
    for i in _tag_:
        if not isinstance(i,int):
            raise TypeError('the expected type is int but received {}'.format(type(i)))
        if i>>16 == 0x0002:
            _header_indices_.append(_tag_.index(i))
    if not _header_indices_:
        raise NotImplementedError('currently dcmio is not capable of dealing with files without dicom header')
    initial_param={}
    initial_param['littleEndian']=True
    initial_param['implicity']=False
    from dcmread import default_encoding
    initial_param['encoding']=default_encoding
    import struct
    result=b''
    for i in _header_indices_:
        if tree.get_branch('tag')[i]==0x00020000:
            continue
        result=result+_attribute_to_bin_(tree,i,**initial_param)
    header_len=tree.get_attributes(tag=0x00020000)
    if not header_len:
        raise NotImplementedError('(0002,0000) is required')
    header_len.set_value(len(result),'value',tag=0x00020000)
    result=bytes(128)+b'DICM'+_attribute_to_bin_(header_len,0,**initial_param)+result
    return result
def convert_encoding(char_set,littleEndian):
    from dcmread import python_encoding
    if char_set in python_encoding:
        return python_encoding[char_set]
    else:
        from dcmread import default_encoding
        return default_encoding
def _data_to_bin_(tree,**kwargs):
    _required_param_=('littleEndian','implicity','encoding')
    _param_={}
    for i in tree._dicom_branches_:
        if i not in tree._get_branches_():
            raise TypeError('the dtree instance does not hold the structure of dicom')
    if tree._is_duplicated_branch_():
        from error import DuplicatedBranchError
        raise DuplicatedBranchError()
    if not tree._is_equal_length_():
        from error import LengthNotEqual
        raise LengthNotEqual()
    imp_le=tree.get_value(tag=0x00020010)
    _specific_char_=False
    if imp_le:
        _param_['littleEndian']=('Little Endian' in imp_le)
        _param_['implicity']=('Implicit' in imp_le)
        char_set=tree.get_value(tag=0x00080005)
        if char_set:
            _specific_char_=True
            _param_['encoding']=convert_encoding(char_set,_param_['littleEndian'])
        else:
            raise NotImplementedError('The (0008,0005) is required')
    elif kwargs:
        for i in _required_param_:
            if i not in kwargs.keys():
                raise NotImplementedError('the implicity and endianness are necessary at the moment')
        for i in _required_param_:
            _param_[i]=kwargs[i]
    else:
        raise NotImplementedError('the implicity, endianness and encoding are necessary at the moment')
    _tag_=tree.get_branch('tag')
    _data_indices_=[]
    for i in _tag_:
        if not isinstance(i,int):
            raise TypeError('the expected type is int but received {}'.format(type(i)))
        if not i>>16 == 0x0002:
            _data_indices_.append(_tag_.index(i))
    if not _data_indices_:
        raise NotImplementedError('currently dcmio is not capable of dealing with files without dataset')
    result=b''
    for i in _data_indices_:
        if _specific_char_:
            from dcmread import default_encoding
            result=result+_attribute_to_bin_(tree,i,littleEndian=True,implicity=_param_['implicity'],encoding=default_encoding)
            _specific_char_=False
        else:
            result=result+_attribute_to_bin_(tree,i,**_param_)
    return result
def write(tree,*args,**kwargs):
    _neccessary_input_=('outpath','filename')
    config={}
    for i in _neccessary_input_:
        if i not in kwargs.keys():
            raise KeyError('an argument {} is missing in the passed arguments'.format(i))
    _header_bin_=_header_to_bin_(tree)
    _data_bin_=_data_to_bin_(tree)
    _bin_=_header_bin_+_data_bin_
    import os
    with open(os.path.join(kwargs['outpath'],kwargs['filename']),'wb') as filewriter:
        filewriter.write(_bin_)


def convert_num(**kwargs):
    _required_param_=('littleEndian','value','struct_format')
    for i in _required_param_:
        if i not in kwargs.keys():
            raise NotImplementedError('The required parameters are {}'.format(_required_param_)+' but received {}'.format(kwargs))
    littleEndian=kwargs['littleEndian']
    value=kwargs['value']
    struct_format=kwargs['struct_format']
    end_char='><'[littleEndian]
    from struct import calcsize
    unit_size=calcsize('='+struct_format)
    from struct import pack
    if isinstance(value,list):
        leng=len(value)
        format_string='%c%u%c'%(end_char,leng,struct_format)
        result=pack(format_string,*value)
    elif isinstance(value,int):
        format_string='%c%c'%(end_char,struct_format)
        result=pack(format_string,value)
    else:
        result=b''
    return result
def convert_str(padding=' ',**kwargs):
    _required_param_=('value','encoding',)
    for i in _required_param_:
        if i not in kwargs.keys():
            raise NotImplementedError('Required parameters are {}'.format(_required_param_)+' but received {}'.format(kwargs))
    value=kwargs['value']
    encoding=kwargs['encoding']
    if not isinstance(value,str):
        value=str(value)
    if len(value)%2!=0:
        value=value+padding
    result=value.encode(encoding,'strict')
    return result


def convert_OB(**kwargs):
    _required_param_=('value',)
    for i in _required_param_:
        if i not in kwargs.keys():
            raise NotImplementedError('Require a value to be packed')
    return kwargs['value']
def convert_DT(**kwargs):
    _required_param_=('value','encoding')
    for i in _required_param_:
        if i not in kwargs.keys():
            raise NotImplementedError('Required parameters are {}'.format(_required_param_)+' but received {}'.format(kwargs))
    value=kwargs['value']
    encoding=kwargs['encoding']
    if isinstance(value,list):
        if len(value)==0:
            return b''
        else:
            result=value[0].encode(encoding)
            for i in value[1:]:
                result=result+'\\'+str(i).encode(encoding)
    else:
        result=str(value).encode(encoding)
    return result
def convert_UN(**kwargs):
    _required_param_=('value',)
    for i in _required_param_:
        if i not in kwargs.keys():
            raise NotImplementedError('Required parameters are {}'.format(_required_param_)+' but received {}'.format(kwargs))
    return kwargs['value']
def convert_AT(**kwargs):
    _required_param_=('value','littleEndian')
    for i in _required_param_:
        if i not in kwargs.keys():
            raise NotImplementedError('Required parameters are {}'.format(_required_param_)+' but received {}'.format(kwargs))
    if kwargs['littleEndian']:
        struct_format='<HH'
    else:
        struct_format='>HH'
    from struct import Struct
    _pack_=Struct(struct_format).pack
    return _pack_(int(kwargs['value'])>>16,int(kwargs['value'])&0xffff)
def convert_SQ(**kwargs):
    _required_param_=('value','littleEndian','implicity','encoding')
    for i in _required_param_:
        if i not in kwargs.keys():
            raise NotImplementedError('Required parameters are {}'.format(_required_param_)+' but received {}'.format(kwargs))
    if not isinstance(kwargs['value'],list):
        raise NotImplementedError('The value field of sequence must be a list but received {}'.format(type(kwargs['value'])))
    result=b''
    for i in kwargs['value']:
        result=result+convert_item(i,**kwargs)
    return result
def convert_item(item,**kwargs):
    _required_param_=('implicity','littleEndian','encoding')
    for i in _required_param_:
        if i not in kwargs.keys():
            raise NotImplementedError('Required parameters are {}'.format(_required_param_)+' but received {}'.format(kwargs))
    if not isinstance(item,DTree):
        raise NotImplementedError('Required type DTree but received {}'.format(type(item)))
    result=_data_to_bin_(item,**kwargs)
    end_char='><'[kwargs['littleEndian']]
    struct_param=end_char+'HHL'
    leng=len(result)
    from struct import Struct
    result=Struct(struct_param).pack(0xfffe,0xe000,leng)+result
    return result
def convert_UI(**kwargs):
    return convert_str(padding='\0',**kwargs)
converters = {
    'UL': (convert_num, 'L'),
    'SL': (convert_num, 'l'),
    'US': (convert_num, 'H'),
    'SS': (convert_num, 'h'),
    'FL': (convert_num, 'f'),
    'FD': (convert_num, 'd'),
    'OF': (convert_num, 'f'),
    'OB': convert_OB,
    'OD': convert_OB,
    'OL': convert_OB,
    'UI': convert_UI,
    'SH': convert_str,
    'DA': convert_DT,
    'TM': convert_DT,
    'CS': convert_str,
    'PN': convert_str,
    'LO': convert_str,
    'IS': convert_str,
    'DS': convert_str,
    'AE': convert_str,
    'AS': convert_str,
    'LT': convert_str,
    'SQ': convert_SQ,
    'UC': convert_str,
    'UN': convert_UN,
    'UR': convert_str,
    'AT': convert_AT,
    'ST': convert_str,
    'OW': convert_OB,
    'OW/OB': convert_OB,  # note OW/OB depends on other items,
    'OB/OW': convert_OB,  # which we don't know at read time
    'OW or OB': convert_OB,
    'OB or OW': convert_OB,
    'US or SS': convert_OB,
    'US or OW': convert_OB,
    'US or SS or OW': convert_OB,
    'US\\US or SS\\US': convert_OB,
    'DT': convert_DT,
    'UT': convert_str,
}
