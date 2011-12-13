import argparse
import fabric.api
import logging
import os
import subprocess
import sys
import zyklop.search
import zyklop.sshconfig


RSYNC_TEMPL = ('rsync -av -e "ssh -l {host.User} -p {host.Port}" '
               '--partial --progress --compress-level=9 '
               '{host.key}:{remotepath} {localdir}')
logger = logging.getLogger('zyklop')
stdout = logging.StreamHandler(sys.__stdout__)
logger.addHandler(stdout)


def sync_storages():
    parser = argparse.ArgumentParser(description="Syncs local storages")
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
        help=("Dry run. Only show what we found."),
        type=bool,
        default=False)

    arguments = parser.parse_args()
    if not arguments.path or arguments.path == '/':
        parser.error(
            "Ehrm - where do you want to search today?")
    sshconfig = zyklop.sshconfig.SSHConfigParser().parse()
    host = sshconfig[arguments.alias]
    fabric.api.env.host_string = '{host.HostName}:{host.Port}'.format(
        host=host)
    search = zyklop.search.FabricSearch(arguments.path, arguments.match)
    results = search.find()
    if arguments.d:
        for i in results:
            logger.warning("Found {0} at level {1}".format(i.path, i.level))
        sys.exit(0)
    else:
        localdir = os.path.abspath(os.getcwd())
        cmd = RSYNC_TEMPL.format(host=host,
                                 remotepath=results[0].path,
                                 localdir=localdir)
        logger.warning(cmd)
        subprocess.Popen(cmd, shell=True)
