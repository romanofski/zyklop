# Copyright (C) 2012, Roman Joost <roman@bromeco.de>
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
import unittest
import StringIO
import zyklop.ssh


class FakeSSHClient(object):

    def __init__(self, cmdoutput):
        self.cmdoutput = cmdoutput

    def exec_command(self, cmd):
        return self.cmdoutput

    def invoke_shell(self):
        return FakeChannel()


class FakeChannel(object):

    def send(self, cmd):
        pass


class TestFakeSFTPClient(unittest.TestCase):

    def create_FakeSSHClient(self, tuples):
        """ returns a fake sshclient which has been instantiated with a
            triple of StringIO instances for stdin, stout, stderr
            respectively.
        """
        client = FakeSSHClient(tuples)
        return zyklop.ssh.FakeSFTPClient(client, 'eggs')

    def test__create_tree(self):
        client = self.create_FakeSSHClient(
            (StringIO.StringIO(),
             StringIO.StringIO("/spam/eggs/baz\n/spam/spam/eggs"),
             StringIO.StringIO()
            )
        )
        self.assertEquals(2, len(client.tree['spam'].children))

    def test_listdir(self):
        client = self.create_FakeSSHClient(
            (StringIO.StringIO(),
             StringIO.StringIO("/spam/eggs/baz\n/spam/spam/eggs"),
             StringIO.StringIO()
            )
        )
        result = client.listdir('/spam')
        self.assertEquals(['/spam/eggs', '/spam/spam'], result)

        result = client.listdir('/spam/eggs')
        self.assertEquals(['/spam/eggs/baz'], result)

    def test_listdir_error(self):
        self.assertRaises(
            OSError,
            self.create_FakeSSHClient,
            (StringIO.StringIO(),
             StringIO.StringIO(""),
             StringIO.StringIO("Something shitty happened")
            )
        )
