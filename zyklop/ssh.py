import os
import paramiko
import re


class SSHRsync(object):

    def __init__(self, sshconfighost, localpath, remotepath):
        self.host = sshconfighost
        self.localpath = localpath
        self.remotepath = remotepath

    def connect(self):
        """ Connects with the remote host via paramiko. Returns
            paramiko.SFTP
        """
        # XXX
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)

        transport = paramiko.Transport((self.host.alias,
                                        int(self.host.Port)))
        transport.connect(username=self.host.User, pkey=mykey)
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp

    def get_remote_fileobj(self, sftp):
        """ Returns paramiko.SFTPFile obj."""
        file = sftp.file(self.remotepath)


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
