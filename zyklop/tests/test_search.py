import os
import os.path
import shutil
import tempfile
import unittest
import zyklop.search


class TestSearch(unittest.TestCase):
    """ Basic test to test the BFS and DFS searches """

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        src = os.path.join(os.path.dirname(__file__), 'testdata')
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

    def test_base(self):
        search = zyklop.search.Search(self.tempdir, '^.*bin/instance')
        # we'll use os.listdir to get the children
        search._get_children_helper = self.children_helper
        child, level = search.find()
        self.assertTrue(child.endswith('folder1/bin/instance'))
        self.assertEquals(level, 2)
