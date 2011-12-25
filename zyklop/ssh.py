import os
import re


class SSHConfigParser(object):
    """ Parses your .ssh/config """

    def __init__(self, path=None):
        if path is None:
            path = os.path.expanduser('~/.ssh/config')
        self.path = path

    def parse(self):
        """ parses the config."""
        result = {}
        confhost = None
        re_template = ('{0}\s(.*)$')
        host = re.compile('^Host\s(.*)$')
        keys = ['HostName', 'User', 'Port']

        with open(self.path, 'r') as f:
            for line in f:
                currenthostkey = (host.match(line) and
                                  host.match(line).groups()[0] or
                                  None)
                if currenthostkey and confhost:
                    result[confhost.key] = confhost
                if currenthostkey:
                    confhost = result.get(currenthostkey,
                                          SSHConfigHost(currenthostkey))
                    continue
                if confhost:
                    for k in keys:
                        match = re.match(re_template.format(k), line)
                        if match:
                            setattr(confhost, k, match.groups()[0])
        result[confhost.key] = confhost
        return result


class SSHConfigHost(object):

    def __init__(self, key, HostName='', Port='22', User=''):
        self.key = key
        self.HostName = HostName
        self.Port = Port
        self.User = User and User or os.environ['LOGNAME']
