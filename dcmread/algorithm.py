from struct import (calcsize,unpack)
from error import (InvalidSQError,InvalidPixelDimension)
from collections import namedtuple
from struct import (Struct, pack, unpack)

from _dicom_dict import DicomDictionary
extra_length_VRs = ('OB', 'OD', 'OF', 'OL', 'OW', 'SQ', 'UC', 'UN', 'UR', 'UT')
default_encoding = "iso8859"
text_VRs = ('SH', 'LO', 'ST', 'LT', 'UC', 'UT')
TEXT_VR_DELIMS = ({0x0d, 0x0a, 0x09, 0x0c})
implicity=False
littleEndian=True
meta_length=0
encoding=default_encoding

rawTag=namedtuple('rawTag',['code','VR','leng','littleEndian','implicity','encoding'])
tag=namedtuple('tag',['code','VR','VM','name'])
attribute=namedtuple('attribute',['tag','val'])

ExplicitVRLittleEndian = '1.2.840.10008.1.2.1'
ImplicitVRLittleEndian = '1.2.840.10008.1.2'
DeflatedExplicitVRLittleEndian = '1.2.840.10008.1.2.1.99'
ExplicitVRBigEndian = '1.2.840.10008.1.2.2'

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

def integratedCode(grp,elm):
    result=grp<<16|elm
    return result

"""This function reads in byte from a DICOM attribute and yield it as a rawAttribute instance

"""
def genRawAttribute(testFile,read):
    global littleEndian
    global implicity
    global meta_length
    global encoding
    local_encoding=encoding
    if testFile.tell()<meta_length:
        local_implicity=False
        local_littleEndian=True
    else:
        local_implicity=implicity
        local_littleEndian=littleEndian
    tagStructUnpack=setStructUnpack(local_implicity,local_littleEndian)
    """
    with open("write.test",'ab') as fileWrite:
        fileWrite.write(str(testFile.tell())+'\n')
        """
    header=read(8)
    if len(header)<8:
        return
    if local_implicity:
        VR=None
        group,elem,leng=tagStructUnpack(header)
    else:
        group,elem,VR,leng=tagStructUnpack(header)
        VR=VR.decode(default_encoding)
        if VR in extra_length_VRs:
            extra_leng=read(4)
            extraLengStructUnpack=setStructUnpack(local_implicity,local_littleEndian,True)
            leng=extraLengStructUnpack(extra_leng)[0]
    code=integratedCode(group,elem)
    if local_implicity and code in DicomDictionary:
        VR=DicomDictionary[code][0]
    elif local_implicity and code not in DicomDictionary:
        VR='UN'
    if leng !=0xFFFFFFFF:  #check if the length is -1 or not. For VR='SQ', length could be -1. not considered yet
        val=read(leng)
        if code==0x00080005:
            encoding=convertEncoding(val,littleEndian)
            if not encoding:
                raise InvalidEncodingError()
        if code==0x00020010:
            val=val.decode(default_encoding)
            if val.endswith(' ') or val.endswith('\x00'):
                val=val[:-1]
            if val==ExplicitVRLittleEndian:
                implicity=False
                littleEndian=True
            elif val==ImplicitVRLittleEndian:
                implicity=True
                littleEndian=True
            elif val==ExplicitVRBigEndian:
                implicity=False
                littleEndian=False
            elif val==DeflatedExplicitVRLittleEndian:
                zipped=read()
                unzipped=zlib.decompress(zipped,-zlib.MAX_WBITS)
                read=getattr(BytesIO(unzipped),"read")
                self.read=read
                implicity=False
                littleEndian=True
            else:
                implicity=True
                littleEndian=True
        raw_tag=rawTag(code,VR,leng,local_littleEndian,local_implicity,local_encoding)
        yield attribute(raw_tag,val)
    else:
        pass
        """To do: include handle for VR="SQ" and error
        if VR == 'SQ':
        elif VR is None:
        else:
            """

def isDICOM(read):
    result=False
    byte=read(128)  # Preamble. Currently useless
    byte=read(4)
    if byte == b"DICM":
        print "This is a DICOM file"
        result=True
    else:
        print "This is not a valid DICOM file"
        result=False
    return result



"""This block reads in the bytes after the magic word and return a dataset of all values except pixels
"""
def dcmRead(file_name):
    result=[]
    with open(file_name,'rb') as testFile:
        read=getattr(testFile,"read")
        __validity__=isDICOM(read)
        if not __validity__:
            raise InvalidDicomError()
        global meta_length
        try:
            while True:
                raw_gen=genRawAttribute(testFile,read)
                raw_attr=next(raw_gen)
                """
                with open("write.test",'ab') as fileWrite:
                    fileWrite.write(str(raw_attr)+'\n')
                    """
                raw_tag=getattr(raw_attr,'tag')
                val=getattr(raw_attr,'val')
                code=getattr(raw_tag,'code')
                VR=getattr(raw_tag,'VR')
                leng=getattr(raw_tag,'leng')
                if code in DicomDictionary:
                    VM=DicomDictionary[code][1]
                    name=DicomDictionary[code][2]
                else:
                    VM=None
                    name=None
                encoding=getattr(raw_tag,"encoding")
                val=readValue(raw_attr)
                if code==0x00020000:
                    meta_length=val+testFile.tell()
                if code==0x00020001:
                    temp_val=val
                    val=[]
                    for i in temp_val:
                        val.append(Struct("B").unpack(i)[0])
                buf_tag=tag(code,VR,VM,name)
                buf_attr=attribute(buf_tag,val)
                """
                with open("write.test",'ab') as fileWrite:
                    fileWrite.write(str(buf_attr)+'\n')
                    """
                result.append(buf_attr)
        except StopIteration:
            pass
    return result



"""This function reads in bytes and return the human-readable value.
"""
def readValue(raw_attr,is_sub=False):
    raw_tag=getattr(raw_attr,'tag')
    code=getattr(raw_tag,'code')
    val=getattr(raw_attr,'val')
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
            result=decodeSQ(raw_attr)
    elif code==0xfffee000:
        raise NotImplementedError("Somethin went wrong in decoding(code). Check it out")
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
        print "length '{}' is not even multiple of {}!".format(len(byte),unit)
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
    result=byte.decode(default_encoding)
    if result and result.endswith('\0'):
        result=result[:-1]
    return result

"""This function returns the date as a string
"""
def decodeDT(byte,littleEndian,struct_format=None):
    val=byte.decode(default_encoding)
    val=val.split("\\")
    if len(val)==1:
        result=val[0]
    else:
        result="".join(str(i) for i in val)
    return result

"""This function decodes the AE values with starting and trailing zeros
"""
def decodeAE(byte,littleEndian,struct_format=None):
    result=byte.decode(default_encoding)
    result=result.strip()
    return result

def setStructUnpack(implicity,littleEndian,extra=False):
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
    tagStructUnpack=tagStruct.unpack
    if extra:
        result=extraLengStructUnpack
    else:
        result=tagStructUnpack
    return result


"""This function reads in bytes of a tag and returns a rawTag instance
"""
def readTag(raw_attr,locator):
    result=None
    littleEndian=getattr(getattr(raw_attr,'tag'),'littleEndian')
    implicity=getattr(getattr(raw_attr,'tag'),'implicity')
    encoding=getattr(getattr(raw_attr,'tag'),'encoding')
    raw_byte=getattr(raw_attr,'val')
    raw_tag=raw_byte[locator:locator+8]
    tagStructUnpack=setStructUnpack(implicity,littleEndian)
    if len(raw_tag)<8:
        return result
    if implicity:
        VR=None
        group,elem,leng=tagStructUnpack(raw_tag)
    else:
        group,elem,VR,leng=tagStructUnpack(raw_tag)
        VR=VR.decode(default_encoding)
        if VR in extra_length_VRs:
            extra_leng=raw_byte[locator+8:locator+12]
            extraLengStructUnpack=setStructUnpack(implicity,littleEndian,True)
            leng=extraLengStructUnpack(extra_leng)[0]
    code=integratedCode(group,elem)
    if implicity:
        if code in DicomDictionary:
            VR=DicomDictionary[code][0]
        else:
            VR='UN'
    result=rawTag(code,VR,leng,littleEndian,implicity,encoding)
    return result

"""This function takes in a rawTag instance and returns a tag instance
"""
def finTag(raw_tag):
    result=None
    code=getattr(raw_tag,'code')
    VR=getattr(raw_tag,'VR')
    if code in DicomDictionary:
        VM=DicomDictionary[code][1]
        name=DicomDictionary[code][2]
    else:
        VM=None
        name=None
    result=tag(code,VR,VM,name)
    return result

"""This function reads in raw_tag, raw_attr and locator, returns a rawAttribute instance of the sub attribute
"""
def readRawSubAttr(raw_attr,raw_tag,locator):
    result=None
    leng=getattr(raw_tag,'leng')
    raw_byte=getattr(raw_attr,'val')
    raw_val=raw_byte[locator:locator+leng]
    result=attribute(raw_tag,raw_val)
    return result

"""This function reads in bytes of a sequence and returns a dataset instance
"""
def decodeSQ(raw_attr):
    result=[]
    result.append([])
    leng_max=getattr(getattr(raw_attr,'tag'),'leng')
    locator=0
    while locator<leng_max:
        raw_tag=readTag(raw_attr,locator)
        locator=locator+8
        fin_tag=finTag(raw_tag)
        if getattr(raw_tag,'code')==0xfffee000:
            result[len(result)-1].append(attribute(fin_tag,None))
            continue
        if getattr(raw_tag,'VR')=='SQ':
            result[len(result)-1].append(attribute(fin_tag,None))
            result.append([])
            continue
        raw_attr_sub=readRawSubAttr(raw_attr,raw_tag,locator)
        val_sub=readValue(raw_attr_sub,is_sub=True)
        result[len(result)-1].append(attribute(fin_tag,val_sub))
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
        print "Expect length for AT to be multiple of 4"
    else:
        val=[convertCode(byte,littleEndian,start=x) for x in range(0,leng,4)]
        result=''.join(str(x) for x in val)
    return result

"""This function converts the encoding string decoded by decodeStr()
   If receives False, assume the default encoding
"""
def convertEncoding(byte,littleEndian):
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
def readPix(pix_attr,width,height):
    result=[]
    raw_pix=getattr(pix_attr,'val')
    locator=0
    pixUnpack=Struct('<h').unpack
    for i in range(0,height):
        result.append([])
        for j in range(0,width):
            result[len(result)-1].append(pixUnpack(raw_pix[locator:locator+2])[0])
            locator=locator+2
    if locator!=2*width*height:
        print locator
        print width
        print height
        raise InvalidPixelDimension('The readPix method is broken')
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
