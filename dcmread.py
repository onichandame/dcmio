from struct import (calcsize,unpack)
from error import (InvalidDicomError,InvalidSQError,InvalidPixelDimension,ItemNotFound,VRNotSpecified)
from collections import namedtuple
from struct import (Struct, pack, unpack)
from dtree import DTree

from _dicom_dict import DicomDictionary
extra_length_VRs = ('OB', 'OD', 'OF', 'OL', 'OW', 'SQ', 'UC', 'UN', 'UR', 'UT')
default_encoding = "iso8859"
text_VRs = ('SH', 'LO', 'ST', 'LT', 'UC', 'UT')
TEXT_VR_DELIMS = ({0x0d, 0x0a, 0x09, 0x0c})
implicity=False
littleEndian=True
meta_length=0
encoding=default_encoding
from _uid_dict import UID_dictionary

raw_info=namedtuple('raw_info',('tag','VR','leng',))
_branches_=('tag','VR','VM','name','value')
attribute=namedtuple('attribute',_branches_)

python_encoding = {

    # default character set for DICOM
    '': default_encoding,

    # alias for latin_1 too (iso_ir_6 exists as an alias to 'ascii')
    'ISO_IR 6': default_encoding,
    'ISO_IR 13': 'shift_jis',

    # these also have iso_ir_1XX aliases in python 2.7
    'ISO_IR 100': 'latin_1',
    'ISO_IR 101': 'iso8859_2',
    'ISO_IR 109': 'iso8859_3',
    'ISO_IR 110': 'iso8859_4',
    'ISO_IR 126': 'iso_ir_126',  # Greek
    'ISO_IR 127': 'iso_ir_127',  # Arabic
    'ISO_IR 138': 'iso_ir_138',  # Hebrew
    'ISO_IR 144': 'iso_ir_144',  # Russian
    'ISO_IR 148': 'iso_ir_148',  # Turkish
    'ISO_IR 166': 'iso_ir_166',  # Thai
    'ISO 2022 IR 6': 'iso8859',  # alias for latin_1 too
    'ISO 2022 IR 13': 'shift_jis',
    'ISO 2022 IR 87': 'iso2022_jp',
    'ISO 2022 IR 100': 'latin_1',
    'ISO 2022 IR 101': 'iso8859_2',
    'ISO 2022 IR 109': 'iso8859_3',
    'ISO 2022 IR 110': 'iso8859_4',
    'ISO 2022 IR 126': 'iso_ir_126',
    'ISO 2022 IR 127': 'iso_ir_127',
    'ISO 2022 IR 138': 'iso_ir_138',
    'ISO 2022 IR 144': 'iso_ir_144',
    'ISO 2022 IR 148': 'iso_ir_148',
    'ISO 2022 IR 149': 'euc_kr',
    'ISO 2022 IR 159': 'iso-2022-jp',
    'ISO 2022 IR 166': 'iso_ir_166',
    'ISO 2022 IR 58': 'iso_ir_58',
    'ISO_IR 192': 'UTF8',  # from Chinese example, 2008 PS3.5 Annex J p1-4
    'GB18030': 'GB18030',
    'ISO 2022 GBK': 'GBK',  # from DICOM correction CP1234
    'ISO 2022 58': 'GB2312',  # from DICOM correction CP1234
    'GBK': 'GBK',  # from DICOM correction CP1234
}

def integrate_tag(grp,elm):
    result=grp<<16|elm
    return result

def is_dicom(read):
    result=False
    byte=read(128)  # Preamble. Currently useless
    byte=read(4)
    if byte == b"DICM":
        print ("This is a DICOM file")
        result=True
    else:
        print ("This is not a valid DICOM file")
        result=False
    return result

def dcm_read(filename):
    import os
    result=DTree(name=os.path.basename(filename),level=0,index=0)
    for i in _branches_:
        result.add_branch(i)
    with open(filename,'rb') as fp:
        read=getattr(fp,'read')
        if not is_dicom(read):
            raise InvalidDicomError()
        metainfo=read_metainfo(read)
        result.merge(metainfo)
        dataset=read_dataset(read,metainfo)
        result.merge(dataset)
    return result

def read_metainfo(read):
    result=DTree(name='metainfo',level=0)
    for i in _branches_:
        result.add_branch(i)
    implicity=False
    littleEndian=True
    meta_length=0
    locator=0
    encoding=default_encoding
    file_meta_leng=read_attribute_leng(read,implicity=implicity,littleEndian=littleEndian,encoding=encoding,level=0)[0]
    if getattr(file_meta_leng,'tag') != 0x00020000:
        raise InvalidDicomError('The file is either broken or incomplete. Contact the provider of the file for help')
    else:
        result.add_attribute(file_meta_leng)
        meta_length=getattr(file_meta_leng,'value')
    while locator<meta_length:
        attr_leng=read_attribute_leng(read)
        result.add_attribute(attr_leng[0])
        locator=locator+attr_leng[1]
    if result.get_value('value',tag=0x00020002) in UID_dictionary:
        result.set_value(UID_dictionary[result.get_value('value',tag=0x00020002)][0],'value',tag=0x00020002)
    if result.get_value('value',tag=0x00020010) in UID_dictionary:
        result.set_value(UID_dictionary[result.get_value('value',tag=0x00020010)][0],'value',tag=0x00020010)
    return result

def read_dataset(read,metainfo):
    result=DTree()
    if not isinstance(metainfo,DTree):
        raise TypeError('The metainfo passed to dataset reader is not of the type DTree')
    for i in _branches_:
        result.add_branch(i)
    imp_le=metainfo.get_value('value',tag=0x00020010)
    implicity=('Implicit' in imp_le)
    littleEndian=("Little Endian" in imp_le)
    encoding=default_encoding
    charset=read_attribute_leng(read,implicity=implicity,littleEndian=littleEndian,encoding=encoding)
    if getattr(charset[0],'tag') != 0x00080005:
        raise InvalidDicomError('Couldn\'t find the expected (0008,0005) attribute')
    encoding=convert_encoding(getattr(charset[0],'value'),littleEndian)
    result.add_attribute(charset[0])
    try:
        while True:
            attr_leng=read_attribute_leng(read,implicity=implicity,littleEndian=littleEndian,encoding=encoding,level=0)
            if not attr_leng:
                raise StopIteration
            else:
                result.add_attribute(attr_leng[0])
    except StopIteration:
        pass
    return result

def read_attribute_leng(read,**kwargs):
    implicity=False
    littleEndian=True
    encoding=default_encoding
    level=0
    for key,value in kwargs.items():
        if key=='implicity':
            implicity=value
        elif key=='littleEndian':
            littleEndian=value
        elif key=='encoding':
            encoding=value
        elif key=='level':
            level=value
    offset=0
    raw_info_leng=read_raw_meta_leng(read,**kwargs)
    if raw_info_leng==b'':
        return None
    offset=offset+raw_info_leng[1]
    fine_metadata=_fine_metadata_(raw_info_leng[0])
    if getattr(fine_metadata,'VR')!='SQ':
        raw_val=read(getattr(raw_info_leng[0],'leng'))
        offset=offset+getattr(raw_info_leng[0],'leng')
        val=read_value(raw_val,getattr(fine_metadata,'VR'),**kwargs)
    else:
        sqval_leng=read_sequence_leng(read,**dict(kwargs,length=getattr(raw_info_leng[0],'leng')))
        if sqval_leng[1]!=getattr(raw_info_leng[0],'leng'):
            raise InvalidDicomError('Detected a mismatch of the sum of length of items and the length of the sequence')
        offset=offset+getattr(raw_info_leng[0],'leng')
        val=sqval_leng[0]
    return (attribute(getattr(fine_metadata,'tag'),getattr(fine_metadata,'VR'),getattr(fine_metadata,'VM'),getattr(fine_metadata,'name'),val),offset)

def read_sequence_leng(read,**kwargs):
    implicity=False
    littleEndian=True
    encoding=default_encoding
    level=0
    length=0
    for key,value in kwargs.items():
        if key=='implicity':
            implicity=value
        elif key=='littleEndian':
            littleEndian=value
        elif key=='encoding':
            encoding=value
        elif key=='level':
            level=value+1
        elif key=='length':
            length=value
    offset=0
    result=[]
    index=0
    while offset<length: #To do: add support of undefined length
        item_leng=read_item_leng(read,implicity=implicity,littleEndian=littleEndian,encoding=encoding,level=level,index=index)
        result.append(item_leng[0])
        offset=offset+item_leng[1]
        index=index+1
    return (result,offset)

def read_item_leng(read,**kwargs):
    result=DTree()
    for i in _branches_:
        result.add_branch(i)
    offset=0
    implicity=False
    littleEndian=True
    encoding=default_encoding
    level=0
    for key,value in kwargs.items():
        if key=='implicity':
            implicity=value
        elif key=='littleEndian':
            littleEndian=value
        elif key=='encoding':
            encoding=value
        elif key=='level':
            level=value
        elif key=='index':
            index=value
    result.set_metainfo(name='item'+str(index+1),level=level,index=index+1)
    meta_leng=read_raw_meta_leng(read,**kwargs)
    if getattr(meta_leng[0],'tag') != 0xfffee000:
        raise ItemNotFound()
    offset=offset+meta_leng[1]
    item_max_leng=getattr(meta_leng[0],'leng')
    item_offset=0
    while item_offset<item_max_leng:
        attr_leng=read_attribute_leng(read,**kwargs)
        offset=offset+attr_leng[1]
        item_offset=item_offset+attr_leng[1]
        result.add_attribute(attr_leng[0])
    return (result,offset)

def read_raw_meta_leng(read,**kwargs):
    offset=0
    implicity=False
    littleEndian=True
    encoding=default_encoding
    for key,value in kwargs.items():
        if key=='implicity':
            implicity=value
        elif key=='littleEndian':
            littleEndian=value
    raw_metadata=read(8)
    offset=offset+8
    if len(raw_metadata)<8:
        return b''
    tag_struct_unpack=_set_struct_unpack_(implicity,littleEndian)
    if implicity:
        VR=None
        group,elem,leng=tag_struct_unpack(raw_metadata)
    else:
        group,elem,VR,leng=tag_struct_unpack(raw_metadata)
        VR=VR.decode(encoding)
        if VR in extra_length_VRs:
            extra_leng=read(4)
            offset=offset+4
            extra_leng_struct_unpack=_set_struct_unpack_(implicity,littleEndian,True)
            leng=extra_leng_struct_unpack(extra_leng)[0]
    tag=integrate_tag(group,elem)
    if implicity and tag in DicomDictionary:
        VR=DicomDictionary[tag][0]
    elif implicity and tag not in DicomDictionary:
        VR='UN'
    return (raw_info(tag,VR,leng),offset)

def read_value(raw_val,VR,**kwargs):
    implicity=False
    littleEndian=True
    encoding=default_encoding
    level=0
    for key,value in kwargs.items():
        if key=='implicity':
            implicity=value
        elif key=='littleEndian':
            littleEndian=value
        elif key=='encoding':
            encoding=value
    if not VR:
        raise VRNotSpecified()
    if VR not in converters:
        raise NotImplementedError('Unknown Value Representation {}'.format(VR))
    if isinstance(converters[VR],tuple):
        converter,struct_format=converters[VR]
    else:
        converter=converters[VR]
        struct_format=None
    if VR in text_VRs or VR == 'PN':
        result=converter(raw_val,littleEndian,None,encoding)
    else:
        result=converter(raw_val,littleEndian,struct_format)
    return result
"""This function reads in bytes and return the human-readable value.
"""
def readValue(raw_attr,level=None):
    raw_tag=raw_attr[0]
    val=raw_attr[1]
    VR=getattr(raw_tag,'VR')
    encoding=getattr(raw_tag,'encoding')
    littleEndian=getattr(raw_tag,'littleEndian')
    if VR not in converters:
        raise NotImplementedError("Unknown Value Representation '{}'".format(VR))
    if isinstance(converters[VR],tuple):
        converter,struct_format=converters[VR]
    else:
        converter=converters[VR]
        struct_format=None
    if VR in text_VRs or VR == 'PN':
        result=converter(val,littleEndian,None,encoding)
    elif VR == 'SQ':
        if is_sub:
            raise NotImplementedError("Somethin went wrong in decoding(VR). Check it out")
        else:
            result=decodeSQ(raw_attr,level)
    elif tag==0xfffee000:
        raise NotImplementedError("Somethin went wrong in decoding(tag). Check it out")
    else:
        result=converter(val,littleEndian,struct_format)
    return result


"""This function decodes an attribute passed from the caller according to the specified encoding scheme
"""
def decode(attr, encoding):
    if not encoding:
        char_set=default_encoding
    """First check if the attribute is person name which needs special attention
    """
    if attr.VR=="PN": # To do: handle cases where VM not 1 differently
        attr.val.decode(encoding)
    elif attr.VR in text_VRs:
        if isinstance(atr.val,str):
            return
        else:
            attr.val=decodeStr(attr.val,littleEndian,None,encoding)

"""This function decodes raw string in bytes to a list of strings
   If empty or 0, return False
"""
def decodeStr(byte,littleEndian=True,struct_format=None, encoding=default_encoding,delimiter=None):
    if isinstance(encoding,str):
        encoding=[encoding]
    if isinstance(byte,str):
        result=str(byte)
    else:
        try:
            result=byte.decode(encoding[0])
        except UnicodeError:
            result=byte.decode(encoding[0],errors='replace')
    if result:
        if result.endswith(' ') or result.endswith('\x00'):
            result=result[:-1]
            """ To do: handle list of string
                """
    else:
        result=''
    return result

"""This function decodes numbers in the value field. The returned type depends on VR
return str '' if the value is empty
return str 'xxxx' if the value is the only element
return list(str) if the value is a tuple
"""
def decodeNum(byte,littleEndian,struct_format):
    endian_chr='><'[littleEndian]
    unit=calcsize("="+struct_format)
    leng=len(byte)
    if leng%unit!=0:
        print ("length '{}' is not even multiple of {}!".format(len(byte),unit))
    format_string="%c%u%c"%(endian_chr,leng//unit,struct_format)
    val=unpack(format_string,byte)
    if len(val)==0:
        result=''
    elif len(val)==1:
        result=val[0]
    else:
        result=list(val)
    return result

"""This function decodes OB value(PixelData)
"""
def decodeOB(byte,littleEndian,struct_format=None):
    # To do: handle (0002,0001) here
    return byte

"""This function decodes UI values(UID). Even Length
"""
def decodeUI(byte,littleEndian,struct_format=None):
    result=decodeStr(byte,encoding=default_encoding)
    if result and result.endswith('\0'):
        result=result[:-1]
    return result

"""This function returns the date as a string
"""
def decodeDT(byte,littleEndian,struct_format=None):
    val=byte.decode(default_encoding)
    val=val.split("\\")
    if len(val)==1:
        val=val[0]
    return val

"""This function decodes the AE values with starting and trailing zeros
"""
def decodeAE(byte,littleEndian,struct_format=None):
    result=byte.decode(default_encoding)
    result=result.strip()
    return result

def _set_struct_unpack_(implicity,littleEndian,extra=False):
    if littleEndian:
        endian_chr="<"
    else:
        endian_chr=">"
    if implicity:
        tagStruct=Struct(endian_chr+"HHL")
    else:
        tagStruct=Struct(endian_chr+"HH2sH")
        extraLengStruct=Struct(endian_chr+"L")
        extraLengStructUnpack=extraLengStruct.unpack
    tag_struct_unpack=tagStruct.unpack
    if extra:
        result=extraLengStructUnpack
    else:
        result=tag_struct_unpack
    return result


"""This function reads in bytes of a tag and returns a raw_info instance
"""
def _read_raw_info_(raw_attr,locator):
    result=None
    littleEndian=getattr(raw_attr[0],'littleEndian')
    implicity=getattr(raw_attr[0],'implicity')
    encoding=getattr(raw_attr[0],'encoding')
    raw_byte=raw_attr[1]
    raw_tag=raw_byte[locator:locator+8]
    locator=locator+8
    tag_struct_unpack=_set_struct_unpack_(implicity,littleEndian)
    if len(raw_tag)<8:
        return result
    if implicity:
        VR=None
        group,elem,leng=tag_struct_unpack(raw_tag)
    else:
        group,elem,VR,leng=tag_struct_unpack(raw_tag)
        VR=VR.decode(default_encoding)
        if VR in extra_length_VRs:
            extra_leng=raw_byte[locator+8:locator+12]
            locator=locator+4
            extraLengStructUnpack=_set_struct_unpack_(implicity,littleEndian,True)
            leng=extraLengStructUnpack(extra_leng)[0]
    tag=integrate_tag(group,elem)
    if implicity:
        if tag in DicomDictionary:
            VR=DicomDictionary[tag][0]
        else:
            VR='UN'
    result=raw_info(tag,VR,leng,littleEndian,implicity,encoding)
    return (result,locator)

"""This function takes in a raw_info instance and returns a tag instance
"""
def _fine_metadata_(raw_tag):
    result=None
    tag=getattr(raw_tag,'tag')
    VR=getattr(raw_tag,'VR')
    if tag in DicomDictionary:
        VM=DicomDictionary[tag][1]
        name=DicomDictionary[tag][2]
    else:
        VM=None
        name=''
    result=attribute(tag,VR,VM,name,None)
    return result

"""This function reads in raw_tag, raw_attr and locator, returns a rawAttribute instance of the sub attribute
"""
def _read_raw_sub_attr_(raw_attr,raw_info,locator):
    result=None
    leng=getattr(raw_info,'leng')
    raw_byte=raw_attr[1]
    raw_val=raw_byte[locator:locator+leng]
    result=(raw_info,raw_val)
    return result

"""This function reads in bytes of a sequence and returns a dataset instance
"""
def decodeSQ(raw_attr,level):
    result=DTree(name='Sequence',level=level+1)
    for i in _branches_:
        result.add_branch(i)
    leng_max=getattr(getattr(raw_attr[0],'metadata'),'leng')
    locator=0
    while locator<leng_max:
        _raw_info_locator_=_read_raw_info_(raw_attr,locator)
        raw_info=_raw_info_locator_[0]
        locator=_raw_info_locator_[1]
        fin_tag=_fine_metadata_(raw_tag)
        for i in _branches_:
            if i != 'value':
                result.add_leaf(branch=i,value=getattr(fine_metadata,i))
        raw_attr_sub=_read_raw_sub_attr_(raw_attr,raw_info,locator)
        if getattr(raw_tag,'tag')==0xfffee000: # To do: add support for itemization
            continue
        if getattr(raw_tag,'VR')=='SQ':
            result.append(attribute(fin_tag,decodeSQ(raw_attr_sub)))
            locator=locator+getattr(raw_tag,'leng')
            continue
        val_sub=readValue(raw_attr_sub,is_sub=True)
        result.append(attribute(fin_tag,val_sub))
        locator=locator+getattr(raw_tag,'leng')
    if locator!=leng_max:
        raise InvalidSQError('The length of the sequence {} is not equal to the length defined in tag'.format(str(raw_attr)))
    return result

"""return raw bytes for UN(unknown)
"""
def decodeUn(byte,littleEndian,struct_format=None):
    return byte

"""This function decodes the AT(tag) value
"""
def convertCode(byte,littleEndian,start=0):
    if littleEndian:
        struct_format="<HH"
    else:
        struct_format=">HH"
    result=unpack(struct_format,byte[start:start+4])
    return result
def decodeAT(byte,littleEndian,struct_format=None):
    leng=len(byte)
    if leng==4:
        result=convertCode(byte,littleEndian)
    elif leng%4!=0:
        print ("Expect length for AT to be multiple of 4")
    else:
        val=[convertCode(byte,littleEndian,start=x) for x in range(0,leng,4)]
        result=''.join(str(x) for x in val)
    return result

"""This function converts the encoding string decoded by decodeStr()
   If receives False, assume the default encoding
"""
def convert_encoding(byte,littleEndian):
    encoding_list=decodeStr(byte,littleEndian,None,default_encoding,"\\")
    if not encoding_list:
        result=default_encoding
    else:
        try:
            result=[python_encoding[encoding_list]]
        except KeyError:
            result = False#  To do: correct some common typo. 1) hard code correction scheme
                                                   #  2) do smart correction

# To do: handle stand-alone encodings including GBK and BIG5
    return result

"""This function is used only when writing pixel data to csv file
"""
def pix_matrix(*args,**kwargs):
    for key,value in kwargs.items():
        if key=='pixel_data':
            raw_pix=value
        elif key=='width':
            width=value
        elif key=='height':
            height=value
    if not raw_pix or not width or not height:
        raise SyntaxError('pix_matrix did not receive enough arguments')
    result=[]
    locator=0
    pixUnpack=Struct('<h').unpack
    for i in range(0,height):
        result.append([])
        for j in range(0,width):
            result[len(result)-1].append(pixUnpack(raw_pix[locator:locator+2])[0])
            locator=locator+2
    if locator!=2*width*height:
        raise InvalidPixelDimension('The pix_matrix method is broken')
    return result


converters = {
    'UL': (decodeNum, 'L'),
    'SL': (decodeNum, 'l'),
    'US': (decodeNum, 'H'),
    'SS': (decodeNum, 'h'),
    'FL': (decodeNum, 'f'),
    'FD': (decodeNum, 'd'),
    'OF': (decodeNum, 'f'),
    'OB': decodeOB,
    'OD': decodeOB,
    'OL': decodeOB,
    'UI': decodeUI,
    'SH': decodeStr,
    'DA': decodeDT,
    'TM': decodeDT,
    'CS': decodeStr,
    'PN': decodeStr,
    'LO': decodeStr,
    'IS': decodeStr,
    'DS': decodeStr,
    'AE': decodeAE,
    'AS': decodeStr,
    'LT': decodeStr,
    'SQ': decodeSQ,
    'UC': decodeStr,
    'UN': decodeUn,
    'UR': decodeStr,
    'AT': decodeAT,
    'ST': decodeStr,
    'OW': decodeOB,
    'OW/OB': decodeOB,  # note OW/OB depends on other items,
    'OB/OW': decodeOB,  # which we don't know at read time
    'OW or OB': decodeOB,
    'OB or OW': decodeOB,
    'US or SS': decodeOB,
    'US or OW': decodeOB,
    'US or SS or OW': decodeOB,
    'US\\US or SS\\US': decodeOB,
    'DT': decodeDT,
    'UT': decodeStr,
}
