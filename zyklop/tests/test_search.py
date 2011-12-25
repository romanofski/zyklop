import os
import os.path
import re
import shutil
import tempfile
import unittest
import zyklop.search


FAKEFSTREE = {'/': dict(
    folder1=dict(
        bin=dict(instance=dict())
    ),
    folder2=dict(),
    folder3=dict(),
)
}


def get_children(path, tree):
    def walk(path, tree, visited=None):
        if visited == None:
            visited = []
        segm = path.pop()
        if segm == '':
            segm = '/'
        visited.append(segm)
        if path:
            children = walk(path, tree[segm], visited)
        else:
            children = tree[segm].keys()
        children = [os.path.join(*visited + [x]) for x in children]
        return children

    if path == '/':
        segments = ['']
    else:
        segments = path.split('/')
        segments.reverse()
    return walk(segments, tree)


class TestWalkFakeFSTree(unittest.TestCase):

    def test_get_children(self):
        children = get_children('/', FAKEFSTREE)
        self.assertEquals(['/folder3', '/folder2', '/folder1'], children)

        children = get_children('/folder2', FAKEFSTREE)
        self.assertEquals([], children)

        children = get_children('/folder1/bin', FAKEFSTREE)
        self.assertEquals(['/folder1/bin/instance'], children)


class TestSearch(unittest.TestCase):
    """ Basic test to test the BFS and DFS searches """

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        src = os.path.join(os.path.dirname(__file__), 'testdata',
                           'dirtree')
        for item in os.listdir(src):
            shutil.copytree(os.path.join(src, item),
                            os.path.join(self.tempdir, item))
        self.addCleanup(self.cleanTempDir, self.tempdir)

    def cleanTempDir(self, tempdir):
        shutil.rmtree(tempdir)

    def children_helper(self, path):
        if os.path.isdir(path):
            return [os.path.join(path, x) for x in os.listdir(path)]
        return []

    def test_find(self):
        search = zyklop.search.Search(self.tempdir, '^.*bin/instance')
        # we'll use os.listdir to get the children
        search._get_children_helper = self.children_helper
        found = search.find()
        self.assertTrue(len(found), 1)
        self.assertTrue(found[0].path.endswith('folder1/bin/instance'))
        self.assertEquals(found[0].level, 2)

        os.mkdir(os.path.join(self.tempdir, 'folder2', 'bin'))
        search.regexp = re.compile('^.*bin$')
        found = search.find()
        self.assertEquals(len(found), 2)
        self.assertTrue(found[0].path.endswith('folder1/bin'))
        self.assertTrue(found[1].path.endswith('folder2/bin'))

    def test_noresult(self):
        search = zyklop.search.Search(self.tempdir, 'foobarnotexist')
        search._get_children_helper = self.children_helper
        found = search.find()
        self.assertEquals(found, [])
