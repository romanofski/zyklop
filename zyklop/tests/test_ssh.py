import os
import shutil
import tempfile
import unittest
import zyklop.ssh


class TestSSHRSync(unittest.TestCase):

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

    def test_get_hashes_for(self):
        rsync = zyklop.ssh.SSHRsync('dummy', 'localhost')

        hashes = rsync.get_hashes_for(
            os.path.join(self.tempdir, 'folder1', 'etc', 'file1.txt'))
        self.assertTrue(hashes)

        self.assertRaises(IOError, rsync.get_hashes_for,
                          os.path.join(self.tempdir, 'folder1'))
