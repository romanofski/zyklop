import os.path
import re


class SSHConfigParser(object):
    """ Parses your .ssh/config """

    def __init__(self, path=None):
        if path is None:
            self.path = os.path.expanduser('.ssh/config')
        self.path = path

    def parse(self):
        """ parses the config."""
        host = re.compile('^HostName.*')
        username = re.compile('^User.*')
        port = re.compile('^Port.*')

        with open(self.path, 'r') as f:
            for line in f:
                hostmatch = host.match(line)
                usernamematch = username.match(line)
                portmatch = port.match(line)
