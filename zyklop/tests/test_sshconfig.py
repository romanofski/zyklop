import os
import os.path
import unittest
import zyklop.sshconfig


class TestSearch(unittest.TestCase):
    """ Basic test to test the BFS and DFS searches """

    def test_sshparser(self):
        config = os.path.join(os.path.dirname(__file__), 'testdata',
                              'samplesshconfig.cfg')
        search = zyklop.sshconfig.SSHConfigParser(path=config)
        self.assertEquals(search.path, config)

