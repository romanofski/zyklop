import argparse
import logging
import os
import paramiko
import sys
import zyklop.rsync
import zyklop.search


logger = logging.getLogger('zyklop')
stdout = logging.StreamHandler(sys.__stdout__)
logger.addHandler(stdout)


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
        rsync = zyklop.ssh.SSHRsync(hostname, port)
        rsync.sync_file(os.path.join(
            localdir, os.path.basename(result.path)), result.path)
    else:
        print("Nothing found.")
        sys.exit(1)
