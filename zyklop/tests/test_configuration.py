import shutil
import tempfile
import unittest
import zyklop.configuration


class TestSearch(unittest.TestCase):
    """ Basic test to test the BFS and DFS searches """

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def cleanTempDir(self, tempdir):
        shutil.rmtree(tempdir)

    def test_defaultconfig(self):
        config = zyklop.configuration.Configuration()
        self.assertTrue(config.configdir.endswith('.config/zyklop'))

