import os.path
import tempfile
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

    def test_get_type(self):
        rsync = zyklop.ssh.SSHRsync('localhost', 22)
        is_folder = rsync.get_type(os.path.join(self.tempdir, 'folder1'))
        self.assertEquals(zyklop.ssh.DIRECTORY, is_folder)

        is_file = rsync.get_type(os.path.join(self.tempdir,
                                                'folder1', 'etc',
                                                'file1.txt'))
        self.assertEquals(zyklop.ssh.FILE, is_file)

    def test_sync_file(self):
        rsync = zyklop.ssh.SSHRsync('localhost', 22)
        localtemp = tempfile.mkdtemp()
        self.addCleanup(self.cleanTempDir, localtemp)

        # given a folder an IOError is raised
        self.assertRaises(IOError, rsync.sync_file, self.tempdir,
                          'dummy')

        # normal copy
        remotepath = os.path.join(
            self.tempdir, 'folder1', 'etc', 'file1.txt')
        localpath = os.path.join(localtemp, 'file1.txt')
        rsync.sync_file(localpath, remotepath)

        with open(localpath, 'r') as copied:
            self.assertEquals('testdata\n', copied.read())

