import os
import paramiko
import re
import zyklop.rsync


class SSHRsync(object):

    def __init__(self, sshconfighost):
        self.host = sshconfighost

    def connect(self):
        """ Connects with the remote host via paramiko. Returns
            paramiko.SFTP
        """
        mykey = self.get_user_pkey()
        transport = paramiko.Transport((self.host.alias,
                                        int(self.host.Port)))
        transport.connect(username=self.host.User, pkey=mykey)
        self.sftp = paramiko.SFTPClient.from_transport(transport)

    def get_user_pkey(self):
        """ Returns the users private key."""
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        return paramiko.RSAKey.from_private_key_file(privatekeyfile)

    def get_remote_fileobj(self):
        """ Returns paramiko.SFTPFile obj."""
        file = self.sftp.file(self.remotepath)

    def get_hashes_for(self, filepath):
        """ Hashes the local file given by filepath. Needs to be a file
            otherwise an IOError is raised.
        """
        with open(filepath, 'rb') as f:
            return zyklop.rsync.blockchecksums(f)


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
                    result[confhost.alias] = confhost
                if currenthostkey:
                    confhost = result.get(currenthostkey,
                                          SSHConfigHost(currenthostkey))
                    continue
                if confhost:
                    for k in keys:
                        match = re.match(re_template.format(k), line)
                        if match:
                            setattr(confhost, k, match.groups()[0])
        result[confhost.alias] = confhost
        return result


class SSHConfigHost(object):

    def __init__(self, alias, HostName='', Port='22', User=''):
        self.alias = alias
        self.HostName = HostName
        self.Port = Port
        self.User = User and User or os.environ['LOGNAME']
