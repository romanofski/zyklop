import argparse
import logging
import os
import paramiko
import sys
import zyklop.rsync
import zyklop.search


DIRECTORY = 1
FILE = 2


logger = logging.getLogger('zyklop')
stdout = logging.StreamHandler(sys.__stdout__)
logger.addHandler(stdout)


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

    def get_type(self, path):
        """ Does a stat on the remote system to check if we're dealing
        with a directory or file.

        @param path: The path to check on the remote system.
        @type path: str
        @return: Either FOLDER or FILE constant
        @rtype: int
        """
        if self.sftp is None:
            self.connect()

        result = DIRECTORY
        try:
            self.sftp.listdir(path)
        except IOError:
            result = FILE
        return result

    def sync(self, localpath, remotefile):
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


def sync():
    parser = argparse.ArgumentParser(
        description="Uses rsync to sync directories",
        epilog=("Use at your own risk and not in production"
                " environments!!!!".upper()))
    parser.add_argument(
        'alias', type=unicode,
        help="Server alias to connect to, specified in your $HOME/.ssh/config")
    parser.add_argument(
        "path",
        help=("A path in the remote filesystem from where to start the"
              " search. Don't start with the root!"
              " e.g.: /opt"),
        type=str)
    parser.add_argument(
        "match",
        help=("A match string the search is looking for. This can be a"
              " path. Defaults to: filestorage"),
        type=str,
        default="filestorage")
    parser.add_argument(
        "-d",
        "--dry-run",
        dest='dry_run',
        help=("Dry run. Only show what we found."),
        action="store_true")

    arguments = parser.parse_args()
    if not arguments.path or arguments.path == '/':
        parser.error(
            "Ehrm - where do you want to search today?")

    sshconfig = paramiko.SSHConfig()
    sshconfig.parse(open(os.path.expanduser('~/.ssh/config'), 'r'))
    host = sshconfig.lookup(arguments.alias)
    hostname = host.get('hostname')
    port = host.get('port', 22)

    if not hostname:
        parser.error("Can't find configuration"
                     " for given alias: {0} in local ~/ssh/config".format(
                         arguments.alias)
                    )

    search = zyklop.search.Search(
        arguments.path, arguments.match,
        zyklop.search.ParamikoChildNodeProvider(hostname, port))
    result = search.find()
    if arguments.dry_run:
        for i in result:
            logger.warning("Found {0} at level {1}".format(i.path, i.level))
        sys.exit(0)
    elif result:
        localdir = os.path.abspath(os.getcwd())
        rsync = SSHRsync(hostname, port)
        rsync.sync_files(localdir, result.path)
    else:
        print("Nothing found.")
        sys.exit(1)
