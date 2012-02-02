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


class TestFakeSFTPClient(unittest.TestCase):

    def setUp(self):
        stdinoutput = StringIO.StringIO("/spam/eggs/baz\n/spam/spam/eggs")
        client = FakeSSHClient((StringIO.StringIO(),
                                stdinoutput,
                                StringIO.StringIO()))
        self.client = zyklop.ssh.FakeSFTPClient(client, 'eggs')

    def test__create_tree(self):
        self.assertEquals(2, len(self.client.tree['spam'].children))

    def test_listdir(self):
        result = self.client.listdir('/spam')
        self.assertEquals(['/spam/eggs', '/spam/spam'], result)

        result = self.client.listdir('/spam/eggs')
        self.assertEquals(['/spam/eggs/baz'], result)
