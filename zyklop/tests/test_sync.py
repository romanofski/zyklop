import unittest
from zyklop import get_command
from zyklop import search_for_remote_path
import zyklop.search


class TestSync(unittest.TestCase):

    def test_format_command(self):
        kwargs = dict(hostname='localhost',
                      remotepath='/remote',
                      localdir='.',
                      user='roman', port=22)
        cmd = get_command(**kwargs)
        self.assertEqual(8, len(cmd))

        kwargs['remotepath'] = '/file with white space.tar.gz'
        cmd = get_command(**kwargs)
        self.assertEqual(8, len(cmd))

        cmd = get_command(sudo=True, **kwargs)
        self.assertEqual(9, len(cmd))

    def test_search_for_remote_path(self):
        result = search_for_remote_path(dict(), '/foo/bar', False)
        self.assertIsInstance(result[0], zyklop.search.SearchResult)
