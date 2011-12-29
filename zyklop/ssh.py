import logging
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


def create_sftpclient(hostname, port=22):
    mykey = get_user_pkey()
    user = os.environ['LOGNAME']
    transport = paramiko.Transport((hostname, port))
    transport.connect(username=user, pkey=mykey)
    return paramiko.SFTPClient.from_transport(transport)


class SSHRsync(object):

    def __init__(self, sftpclient):
        self.sftpclient = sftpclient
        self.logger = logging.getLogger('zyklop')

    def get_remote_delta(self, filepath, hashes):
        """ Returns paramiko.SFTPFile obj. Raises an IOError if the file
            can not be retrieved or is a directory.
        """
        self.logger.info("Creating Patch {0}".format(filepath))
        file = self.sftpclient.file(filepath)
        return zyklop.rsync.rsyncdelta(file, hashes)

    def get_hashes_for(self, filepath):
        """ Hashes the local file given by filepath. Needs to be a file
            otherwise an IOError is raised.
        """
        checksums = ([], [])
        if os.path.exists(filepath):
            self.logger.info("Hashing {0}".format(filepath))
            with open(filepath, 'rb') as f:
                checksums = zyklop.rsync.blockchecksums(f)
        return checksums

    def get_type(self, path):
        """ Does a stat on the remote system to check if we're dealing
        with a directory or file.

        @param path: The path to check on the remote system.
        @type path: str
        @return: Either FOLDER or FILE constant
        @rtype: int
        """
        result = DIRECTORY
        try:
            self.sftpclient.listdir(path)
        except IOError:
            result = FILE
        return result

    def sync_file(self, localpath, remotepath):
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
                    self.logger.info("Done.")
        else:
            self.sftpclient.get(remotepath, localpath)

    def sync_directories(self, localpath, remotepath):
        if not os.path.exists(localpath):
            os.mkdir(localpath)
        children = self.sftpclient.listdir(remotepath)
        for c in children:
            localfilepath = os.path.join(localpath, c)
            remotefilepath = os.path.join(remotepath, c)
            self.sync(localfilepath, remotefilepath)

    def sync(self, localpath, remotepath):
        """ Synchronises given localpath from remotepath, no matter if
            the remotepath points to a directory or file.
        """
        self.logger.info("{0} => {1}".format(
            localpath, remotepath))
        type = self.get_type(remotepath)
        if type == FILE:
            self.sync_file(localpath, remotepath)
        elif type == DIRECTORY:
            self.sync_directories(localpath, remotepath)
