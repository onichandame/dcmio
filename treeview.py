# coding: utf-8
from __future__ import absolute_import
from util import _delete
from error import EmptySequenceError
def _get_line_(attr,level,is_end):
    lvl_ind='-'
    lead_char='├'
    return_char='└'
    lead_ind='  '
    tag=getattr(attr,'tag')
    name=getattr(tag,'name')
    VR=getattr(tag,'VR')
    code=getattr(tag,'code')
    if is_end:
        lead_char=return_char
    line=lead_ind*level+lead_char+lvl_ind+VR+','+name
    return line

def write_tree(ds,outpath,file_name,level=0):
    if len(ds)==0:
        raise EmptySequenceError('empty sequence is not yet supported') #To do: add support of empty sequence
    if level==0:
        _delete(suffix='treeview.txt',path=outpath,filename=file_name)
        with open(outpath+filename+'-treeview.txt','a') as fileWrite:
            heading='DICOM'+'\r\n'+'|'+'\r\n'
            fileWrite.write(heading)
    for i in ds:
        is_end=False
        if i is ds[-1]:
            is_end=True
        tag=getattr(i,'tag')
        code=getattr(tag,'code')
        VR=getattr(tag,'VR')
        if code==0xfffee000:
            continue
        line = _get_line_(i,level,is_end)
        with open(outpath+'treeview.txt','a') as fileWrite:
            fileWrite.write(line+'\r\n')
        if VR=='SQ':
            printTree(getattr(i,'val'),outpath,level=level+1)
