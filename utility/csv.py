from __future__ import absolute_import
import csv
from .error import EmptyListError
import os

def _delete(fileName,path='./test/'):
    fullName=path+fileName+'.test'
    if not os.path.exists(path):
        os.mkdir(path)
    if os.path.exists(fullName):
        os.remove(fullName)

def writeToCSV(lst,outpath,_is_pixel_):
    import sys
    from dcmread.algorithm import readPix
    if len(lst)==0:
        raise EmptyListError()
    if _is_pixel_:
        _delete('pixel',path=outpath)
        with open(outpath+"pixel.test",'w') as fileWrite:
            writer=csv.writer(fileWrite,delimiter=',')
            pix_attr=None
            for i in lst:
                if getattr(getattr(i,'tag'),'code')==0x00280011:
                    width=int(getattr(i,'val'))
                elif getattr(getattr(i,'tag'),'code')==0x00280010:
                    height=int(getattr(i,'val'))
                elif getattr(getattr(i,'tag'),'code')==0x7fe00010:
                    pix_attr=i
            if not width or not height:
                raise InvalidPixelDimension()
            pix_val=readPix(pix_attr,width,height)
            writer.writerows(pix_val)
        os.rename(outpath+'pixel.test',outpath+'pixel.csv')
    else:
        _delete('header',path=outpath)
        with open(outpath+"header.test",'w') as fileWrite:
            writer=csv.writer(fileWrite,delimiter=',')
            writer.writerow(['Code','VR','VM','Name','Value'])
            for i in lst:
                if getattr(getattr(i,'tag'),'code')!=0x7fe00010:
                    writer.writerow([format(getattr(getattr(i,'tag'),'code'),'08x'),getattr(getattr(i,'tag'),'VR'),getattr(getattr(i,'tag'),'VM'),getattr(getattr(i,'tag'),'name'),getattr(i,'val')])
        os.rename(outpath+'header.test',outpath+'header.csv')
