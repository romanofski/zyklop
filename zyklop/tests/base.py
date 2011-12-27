import os
import shutil
import tempfile
import unittest


class BaseDirectoryTestCase(unittest.TestCase):

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
