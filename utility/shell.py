import getopt
import sys
from error import InputFileError
def get_config():
    sys.path.insert(0,"..")
    from dcmread.algorithm import decodeStr
    result={}
    shortopts='pi:o:t'
    try:
        optlist,args=getopt.getopt(sys.argv[1:],shortopts)
        for key, value in optlist:
            if key=='-p':
                result['pixel']=True
            if key=='-o':
                result['outpath']=decodeStr(value,encoding='utf-8')
            if key=='-i':
                result['filename']=decodeStr(value,encoding='utf-8')
            if key=='-t':
                result['tree']=True
        if 'pixel' not in result:
            result['pixel']=False
        if 'outpath' not in result:
            result['outpath']="./test/"
        if 'filename' not in result:
            raise InputFileError('The input DICOM file is not specified',)
        if 'tree' not in result:
            result['tree']=False
    except getopt.GetoptError as e:
        print 'lol'
        sys.exit(1)
    return result
