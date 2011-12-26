import argparse
import fabric.api
import logging
import os
import subprocess
import sys
import zyklop.search
import zyklop.ssh


SSH_CMD = 'ssh -l {host.User} -p {host.Port}'
RSYNC_TEMPL = ('rsync -av -e '
               '--partial --progress --compress-level=9 '
               '{host.alias}:{remotepath} {localdir}')
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
    sshconfig = zyklop.ssh.SSHConfigParser().parse()
    host = sshconfig[arguments.alias]
    fabric.api.env.host_string = '{host.HostName}:{host.Port}'.format(
        host=host)
    search = zyklop.search.FabricSearch(arguments.path, arguments.match)
    results = search.find()
    if arguments.dry_run:
        for i in results:
            logger.warning("Found {0} at level {1}".format(i.path, i.level))
        sys.exit(0)
    else:
        localdir = os.path.abspath(os.getcwd())
        rsync = zyklop.ssh.SSHRsync(host)
        rsync.sync_files(localdir, results[0].path)
