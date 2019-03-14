#!/usr/bin/env python
# -*- coding: utf-8 -*-
from io import BytesIO
from binascii import (a2b_hex, b2a_hex)
from dcmread import dcm_read
from util import write_to_csv
from shell import get_config
import sys
import time

"""
#This block is used to test the reading of binary files of 2 methods: getattr() and read().
#The result shows no difference

    binFileName="test.dcm"  #  including path
    with open(binFileName,'rb') as testFile:
        parentRead=getattr(testFile,"read")
        result=parentRead()
        with open('./attr.test','wb') as fileAttr:
            fileAttr.write(result)
    with open(binFileName,'rb') as testFile:
        result=testFile.read()
        with open('./read.test','wb') as read:
            read.write(result)
            """

"""
#This block tests the reading of specific bytes.
#The result proves the ability to read dicom files in hex representation at any absolute position of the file.
def bytes2hex(byte):
    hex_string=b2a_hex(byte)
    return " ".join(hex_string[i:i+2] for i in range(0, len(hex_string), 2))
    binFileName="test.dcm"
    with open(binFileName,'rb') as testFile:
        byte=testFile.read(1080)
        with open("hex.test",'w') as fileHex:
            fileHex.write(bytes2hex(byte))
            """

"""
#This block tests the Struct.unpack utility
#The result proves the ability of python to decode values of different endianness
    with open("pack.test",'wb') as filePack:
        filePack.write(pack('<HHL',2,1,4))
    #print unpack('<HHL',pack('<HHL',2,1,4))
    """

def main():
    config=get_config()
    for key,value in config.items():
        if key=='pixel':
            _is_pixel_=value
        if key=='filename':
            file_name=value
        if key=='outpath':
            outpath=value
        if key=='tree':
            if_tree=value
    timer=time.time()
    dcm=dcm_read(file_name)
    print(dcm)
    print ('The reading of dcm file takes {} seconds'.format(time.time()-timer))
    from dcmwrite import write
    write(dcm,outpath='./',filename='write.dcm')
    sys.exit()
    timer=time.time()
    write_to_csv(dcm,outpath,file_name,_is_pixel_)
    print ('The writing to csv files takes {} seconds'.format(time.time()-timer))
    if if_tree:
        from treeview import write_tree
        timer=time.time()
        write_tree(dcm,outpath,file_name)
        print ('The writing to treeview takes {} seconds'.format(time.time()-timer))

if __name__=='__main__':
    main()
