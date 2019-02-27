def _get_line_(attr,level):
    lvl_ind='-'
    lead_char='├'
    return_char='└'
    lead_ind='  '
    tag=getattr(attr,'tag')
    name=getattr(tag,'name')
    VR=getattr(tag,'VR')
    code=getattr(tag,'code')
    line=lead_ind*level+lead_char+lvl_ind+VR+','+name
    return line

def printTree(ds):
    temp_ds=ds
    bak_ds=[]
    level=0
    index=0
    indexlist=[]
    print "DICOM"
    print "|"
    while index<len(temp_ds)+1:
        if index==len(temp_ds):
            if level==0:
                index=index+1
                continue
            else:
                del bak_ds[level]
                del indexlist[level]
                level=level-1
                temp_ds=bak_ds[level]
                index=indexlist[level]
        line = _get_line_(temp_ds[index],level)
        VR=getattr(getattr(temp_ds[index],'tag'),'VR')
        code=getattr(getattr(temp_ds[index],'tag'),'code')
        if VR=='SQ':
            bak_ds.append(temp_ds)
            temp_ds=getattr(temp_ds[index],'val')
            level=level+1
            index=index+1
            indexlist.append(index)
            index=0
        elif code==0xfffee000:
            index=index+1
            continue
        else:
            index=index+1
        print line
