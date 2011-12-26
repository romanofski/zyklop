import os
import shutil
import tempfile
import unittest
import zyklop.ssh


class TestSSHConfigParser(unittest.TestCase):

    def test_sshparser(self):
        config = os.path.join(os.path.dirname(__file__), 'testdata',
                              'samplesshconfig.cfg')
        parser = zyklop.ssh.SSHConfigParser(path=config)
        self.assertEquals(parser.path, config)

        parsed = parser.parse()
        self.assertEquals(len(parsed), 7)

        expected = ['zopedev', 'devel', 'wilber',
                     'gecko', 'svn.berlios.de',
                     'cmswiki.foobar.com.au',
                     'svn.zope.org']
        self.assertEquals(sorted(parsed.keys()), sorted(expected))

        host = parsed['devel']
        self.assertEquals(host.HostName, 'dev.foobar.com')
        self.assertEquals(host.Port, '22')
        self.assertEquals(host.User, 'rj')

        self.assertEquals(parsed['wilber'].User, os.environ['LOGNAME'])


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
        rsync = zyklop.ssh.SSHRsync(
            zyklop.ssh.SSHConfigHost('dummy', 'localhost'))

        hashes = rsync.get_hashes_for(
            os.path.join(self.tempdir, 'folder1', 'etc', 'file1.txt'))
        self.assertTrue(hashes)

        self.assertRaises(IOError, rsync.get_hashes_for,
                          os.path.join(self.tempdir, 'folder1'))
