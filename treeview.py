# coding: utf-8
from __future__ import absolute_import
from util import _delete
from error import EmptySequenceError
from dtree import DTree
def _get_line_(ds,index,is_end):
    lvl_ind='-'
    lead_char='├'
    return_char='└'
    lead_ind='  '
    level=ds.get_metainfo()['level']
    tag=ds.get_branch('tag')[index]
    name=ds.get_branch('name')[index]
    VR=ds.get_branch('VR')[index]
    if is_end:
        lead_char=return_char
    line=lead_ind*level+lead_char+lvl_ind+VR+','+name
    return line

def write_tree(ds,outpath,file_name):
    if len(ds)==0:
        raise EmptySequenceError('empty DTree is not yet supported') #To do: add support of empty sequence
    elif ds.get_length()==0:
        raise EmptySequenceError('DTree with empty branches is not yet supported')
    level=ds.get_metainfo()['level']
    if level==0:
        _delete(suffix='treeview.txt',path=outpath,filename=file_name)
        with open(outpath+file_name+'-treeview.txt','a') as fileWrite:
            heading='DICOM'+'\r\n'+'|'+'\r\n'
            fileWrite.write(heading)
    for i in range(ds.get_length()):
        is_end=False
        if (i+1) == ds.get_length():
            is_end=True
        tag=ds.get_branch('tag')[i]
        VR=ds.get_branch('VR')[i]
        line = _get_line_(ds,i,is_end)
        with open(outpath+file_name+'-treeview.txt','a') as fileWrite:
            fileWrite.write(line+'\r\n')
        if VR=='SQ':
            if isinstance(ds.get_value(i),list):
                for j in ds.get_value(i):
                    write_tree(j,outpath,file_name)
