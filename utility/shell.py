import getopt
import sys
from error import InputFileError
def get_config():
    sys.path.insert(0,"..")
    from dcmread.algorithm import decodeStr
    result={}
    shortopts='pi:'
    try:
        optlist,args=getopt.getopt(sys.argv[1:],shortopts)
        for key, value in optlist:
            if key=='-p':
                result['pixel']=True
            if key=='-i':
                result['filename']=decodeStr(value,encoding='utf-8')
        if 'pixel' not in result:
            result['pixel':False]
        if 'filename' not in result:
            raise InputFileError('The input DICOM file is not specified',)
    except getopt.GetoptError as e:
        sys.exit(1)
    return result
