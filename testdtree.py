import common.dtree

tree=common.dtree.DTree(name='testtree')
print 'initial tree='+str(tree)
print 'initial tree info='+str(tree.get_metainfo())
tree.add_branch('test')
print 'branch info='+str(tree.get_branch('test').get_metainfo())
print 'final tree='+str(tree)
print 'final tree info='+str(tree.get_metainfo())
