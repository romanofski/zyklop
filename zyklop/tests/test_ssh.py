import os
import os.path
import unittest
import zyklop.ssh


class TestSearch(unittest.TestCase):
    """ Basic test to test the BFS and DFS searches """

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
