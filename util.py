from __future__ import absolute_import
import csv
from error import EmptyListError
from dtree import DTree
import os

def _delete(*args,**kwargs):
    for key,value in kwargs.items():
        if key=='suffix':
            suffix=value
        elif key=='path':
            path=value
        elif key=='filename':
            filename=value
    if not suffix or not path or not filename:
        raise SyntaxError('The _delete function requires all arguments to be defined')
    fullname=path+filename+'-'+suffix
    if not os.path.exists(path):
        os.mkdir(path)
    if os.path.exists(fullname):
        os.remove(fullname)

def write_to_csv(_tree_,outpath,file_name,_is_pixel_):
    from copy import deepcopy
    tree=deepcopy(_tree_)
    _indices_=tree._get_index_(VR='SQ')
    if _indices_:
        for i in _indices_:
            tree.set_value(len(tree.get_value(i)),'value',i)
    file_name=os.path.basename(file_name)
    tree.del_attributes(tag=0x7fe00010)
    if len(tree)==0:
        raise EmptyListError()
    _delete(suffix='header.csv',path=outpath,filename=file_name)
    fullname=outpath+file_name+'-header.csv'
    with open(fullname,'w') as fileWrite:
        writer=csv.writer(fileWrite,delimiter=',')
        _branches_=[]
        for i in tree:
            _branches_.append(i.get_metainfo()['name'])
        writer.writerow(_branches_)
        for i in range(tree.get_length()):
            lst=[]
            for j in tree:
                lst.append(j[i])
            writer.writerow(lst)
    if _is_pixel_:
        _delete(suffix='pixel.csv',filename=file_name,path=outpath)
        with open(outpath+file_name+"-pixel.csv",'w') as fileWrite:
            writer=csv.writer(fileWrite,delimiter=',')
            pix_attr=None
            width=_tree_.get_value(tag=0x00280011)
            height=_tree_.get_value(tag=0x00280010)
            pixel_data=_tree_.get_value(tag=0x7fe00010)
            from dcmread import pix_matrix
            pix_val=pix_matrix(pixel_data=pixel_data,width=width,height=height)
            writer.writerows(pix_val)
