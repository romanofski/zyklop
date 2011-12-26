import os
import paramiko
import zyklop.rsync


class SSHRsync(object):

    sftp = None

    def __init__(self, hostname, port, user=None):
        self.hostname = hostname
        self.port = port
        self.user = user and user or os.environ['LOGNAME']

    def connect(self):
        """ Connects with the remote host via paramiko. Returns
            paramiko.SFTP
        """
        mykey = self.get_user_pkey()
        transport = paramiko.Transport((self.hostname, self.port))
        transport.connect(username=self.user, pkey=mykey)
        self.sftp = paramiko.SFTPClient.from_transport(transport)

    def get_user_pkey(self):
        """ Returns the users private key."""
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        return paramiko.RSAKey.from_private_key_file(privatekeyfile)

    def get_remote_delta(self, filepath, hashes):
        """ Returns paramiko.SFTPFile obj."""
        if self.sftp is None:
            self.connect()
        file = self.sftp.file(filepath)
        return zyklop.rsync.rsyncdelta(file, hashes)

    def get_hashes_for(self, filepath):
        """ Hashes the local file given by filepath. Needs to be a file
            otherwise an IOError is raised.
        """
        checksums = ([], [])
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                checksums = zyklop.rsync.blockchecksums(f)
        return checksums

    def sync_files(self, localpath, remotefile):
        if os.path.isdir(localpath):
            localfile = os.path.join(localpath,
                                     os.path.basename(remotefile))
        else:
            localfile = localpath

        hashes = self.get_hashes_for(localfile)
        delta = self.get_remote_delta(remotefile, hashes)
        newfile = localfile + '.sync'
        if not os.path.exists(localfile):
            with open(localfile, 'w') as unpatched:
                unpatched.close()

        with open(localfile, 'r') as unpatched:
            with open(newfile, 'wb') as saveto:
                zyklop.rsync.patchstream(unpatched, saveto, delta)
                saveto.close()
                os.rename(newfile, localfile)
