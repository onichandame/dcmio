import dtree

tree=dtree.DTree(name='testtree')
print(tree)
_branches_=('tag','VR','VM','name','value')
for i in _branches_:
    tree.add_branch(i)
for i in range(1,5):
    for j in _branches_:
        tree.add_leaf(branch=j,value=j+str(i))
search=tree.get_attributes(tag='tag3:tag1',VR='VR1',value='value4')
print (search)
