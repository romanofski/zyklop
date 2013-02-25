from zyklop.command import get_command
from zyklop.command import get_username
from zyklop.command import logger
from zyklop.command import search_for_remote_path
from zyklop.command import sync
from zyklop.command import ERROR_NO_SSH_CONFIGFILE
import mock
import os.path
import testfixtures
import unittest
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

    @mock.patch.dict('os.environ', dict(LOGNAME='environuser'))
    def test_get_username(self):
        self.assertEqual('testuser',
                         get_username(dict(user='testuser')))
        self.assertEqual('environuser',
                         get_username(dict(username='testuser')))
        self.assertEqual('environuser', get_username())

    @mock.patch('sys.argv', ['zyklop', 'ignored:path', '.'])
    @mock.patch.object(os.path, 'exists')
    @testfixtures.log_capture()
    def test_no_ssh_config(self, fakeexists, lcapture):
        fakeexists.return_value = False
        self.assertRaises(SystemExit, sync)
        lcapture.check((logger.name, 'ERROR', ERROR_NO_SSH_CONFIGFILE))
