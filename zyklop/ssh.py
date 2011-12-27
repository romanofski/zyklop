import os
import paramiko
import zyklop.rsync
import zyklop.search


DIRECTORY = 1
FILE = 2


def get_user_pkey():
    """ Returns the users private key."""
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    return paramiko.RSAKey.from_private_key_file(privatekeyfile)


def connect(func):
    def wrapped(*args, **kwargs):
        obj = args[0]
        mykey = get_user_pkey()
        user = os.environ['LOGNAME']
        transport = paramiko.Transport((obj.hostname, obj.port))
        transport.connect(username=user, pkey=mykey)
        sftp = paramiko.SFTPClient.from_transport(transport)
        kwargs.update(sftpclient=sftp)
        return func(*args, **kwargs)
    return wrapped


class SSHRsync(object):

    sftp = None

    def __init__(self, hostname, port, user=None):
        self.hostname = hostname
        self.port = port

    @connect
    def get_remote_delta(self, filepath, hashes, sftpclient):
        """ Returns paramiko.SFTPFile obj. Raises an IOError if the file
            can not be retrieved or is a directory.
        """
        file = sftpclient.file(filepath)
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

    @connect
    def get_type(self, path, sftpclient):
        """ Does a stat on the remote system to check if we're dealing
        with a directory or file.

        @param path: The path to check on the remote system.
        @type path: str
        @return: Either FOLDER or FILE constant
        @rtype: int
        """
        result = DIRECTORY
        try:
            sftpclient.listdir(path)
        except IOError:
            result = FILE
        return result

    @connect
    def sync_file(self, localpath, remotepath, sftpclient):
        """ Syncs a given local file from the given remotepath.

        @param localpath: Path to the local file. If the file does not
                          exist locally, it will be created by an sftp
                          get. If the path points to a local directory
                          an IOError is raised.
        @type localpath: str
        @param remotepath: Path to the remote file, which should be a
                           file, otherwise IOError is raised.
        """
        if os.path.exists(localpath):
            if os.path.isdir(localpath):
                raise IOError("{0} points to a directory.".format(localpath))

            hashes = self.get_hashes_for(localpath)
            delta = self.get_remote_delta(remotepath, hashes)
            newfile = localpath + '.sync'
            if not os.path.exists(localpath):
                with open(localpath, 'w') as unpatched:
                    unpatched.close()

            with open(localpath, 'r') as unpatched:
                with open(newfile, 'wb') as saveto:
                    zyklop.rsync.patchstream(unpatched, saveto, delta)
                    saveto.close()
                    os.rename(newfile, localpath)
        else:
            sftpclient.get(remotepath, localpath)
