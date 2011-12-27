import os.path
import zyklop.ssh
import zyklop.tests.base


class TestSSHRSync(zyklop.tests.base.BaseDirectoryTestCase):

    def test_get_hashes_for(self):
        rsync = zyklop.ssh.SSHRsync('dummy', 'localhost')

        hashes = rsync.get_hashes_for(
            os.path.join(self.tempdir, 'folder1', 'etc', 'file1.txt'))
        self.assertTrue(hashes)

        self.assertRaises(IOError, rsync.get_hashes_for,
                          os.path.join(self.tempdir, 'folder1'))
