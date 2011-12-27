import os.path
import paramiko
import re


class SearchResult(object):

    def __init__(self, path, level):
        self.path = path
        self.level = level

    def __repr__(self):
        return '<{0} object {1}>'.format(
            self.__class__.__name__, self.path)


class Search(object):

    maxdepth = 4

    def __init__(self, top, regexp, childnodeprovider):
        self.top = top
        self.regexp = re.compile(regexp)
        self.childnodeprovider = childnodeprovider

    def find(self, children=None, visited=None, level=0):
        """ BFS to find a zope sandbox."""
        if level == self.maxdepth:
            return []
        if not children:
            children = self.childnodeprovider.get_children(self.top)

        if visited is None:
            visited = []
        else:
            for c in visited:
                children += self.childnodeprovider.get_children(c)

        while children:
            child = children.pop()
            if child in visited:
                continue
            if self.regexp.search(child):
                return SearchResult(child, level)
            visited.append(child)

        level += 1
        return self.find(children, visited, level=level)


class DirectoryChildNodeProvider(object):

    def get_children(self, abspath):
        if not abspath.startswith('/'):
            raise ValueError(
                "abspath parameter needs to be an absolute path: {0}".format(
                    abspath))
        return self._get_children_helper(abspath)

    def _get_children_helper(self, abspath):
        """ Helper function which returns a list of children. """
        raise NotImplemented("Must be implemented in sublcasses.")


def connect(func):
    def wrapped(*args):
        childnodeprovider = args[0]
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        ssh.connect(hostname=childnodeprovider.hostname,
                    port=childnodeprovider.port, pkey=mykey)
        childnodeprovider.ssh_client = ssh
        return func(*args)
    return wrapped


class ParamikoChildNodeProvider(DirectoryChildNodeProvider):

    ssh_client = None

    def __init__(self, hostname, port):
        # XXX perhaps we can use an sshconfig dict?
        self.hostname = hostname
        self.port = port

    @connect
    def _get_children_helper(self, abspath):
        cmd = "ls -1 {0}".format(abspath)
        stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
        children = [os.path.join(abspath, c) for c in re.split('\s',
                                                               stdout.read())]
        return children
