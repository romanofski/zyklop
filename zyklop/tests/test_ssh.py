# Copyright (C) 2011-2012, Roman Joost <roman@bromeco.de>
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.  If not, see
# <http://www.gnu.org/licenses/>.
import os.path
import tempfile
import zyklop.ssh
import zyklop.tests.base


class TestSSHRSync(zyklop.tests.base.BaseDirectoryTestCase):

    def setUp(self):
        super(TestSSHRSync, self).setUp()
        self.rsync = zyklop.ssh.SSHRsync(
            zyklop.ssh.create_sftpclient('localhost', 22))

    def test_get_hashes_for(self):
        hashes = self.rsync.get_hashes_for(
            os.path.join(self.tempdir, 'folder1', 'etc', 'file1.txt'))
        self.assertTrue(hashes)

        self.assertRaises(IOError, self.rsync.get_hashes_for,
                          os.path.join(self.tempdir, 'folder1'))

    def test_get_type(self):
        is_folder = self.rsync.get_type(os.path.join(self.tempdir,
                                                     'folder1'))
        self.assertEquals(zyklop.ssh.DIRECTORY, is_folder)

        is_file = self.rsync.get_type(os.path.join(self.tempdir,
                                                   'folder1', 'etc',
                                                   'file1.txt'))
        self.assertEquals(zyklop.ssh.FILE, is_file)

    def test_sync_file(self):
        localtemp = tempfile.mkdtemp()
        self.addCleanup(self.cleanTempDir, localtemp)

        # given a folder an IOError is raised
        self.assertRaises(IOError, self.rsync.sync_file, self.tempdir,
                          'dummy')

        # normal copy
        remotepath = os.path.join(
            self.tempdir, 'folder1', 'etc', 'file1.txt')
        localpath = os.path.join(localtemp, 'file1.txt')
        self.rsync.sync_file(localpath, remotepath)

        with open(localpath, 'r') as copied:
            self.assertEquals('testdata\n', copied.read())

    def test_sync_directories(self):
        localtemp = tempfile.mkdtemp()
        self.addCleanup(self.cleanTempDir, localtemp)

        remotepath = os.path.join(self.tempdir, 'folder1')
        self.rsync.sync_directories(localtemp, remotepath)

        self.assertEquals(['bin', 'etc'], sorted(os.listdir(localtemp)))
        self.assertEquals(['instance'],
                          os.listdir(os.path.join(localtemp, 'bin')))
        self.assertEquals(['file1.txt', 'file2.txt'],
                          sorted(os.listdir(os.path.join(localtemp, 'etc'))))
