# Copyright (C) 2011-2012, Roman Joost <roman@bromeco.de>
#
# This library is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.  If not, see
# <http://www.gnu.org/licenses/>.
import argparse
import logging
import os
import paramiko
import subprocess
import sys
import zyklop.search
import zyklop.ssh


SSH_CMD = 'ssh -l {user} -p {port}'
RSYNC_TEMPL = ('rsync -av -e '
               '--partial --progress --compress-level=9 '
               '{hostname}:{remotepath} {localdir}')


logger = logging.getLogger('zyklop')
stdout = logging.StreamHandler(sys.stdout)
stdout.setFormatter(logging.Formatter())
logger.addHandler(stdout)
logger.setLevel(logging.INFO)


def sync():
    """ Entry point which parses given arguments, searches for a
        file/directory to sync on the remote server and passes it on to
        rsync.
    """
    parser = argparse.ArgumentParser(
        description="Uses rsync to sync directories",
        epilog=("Use at your own risk and not in production"
                " environments!!!!".upper()))
    parser.add_argument(
        "host",
        help=("A hostname/ssh alias"),
        type=str)
    parser.add_argument(
        "match",
        help=("A match string the search is matching every file- and"
              " directory name with. Each directory on the remote server"
              " is split into segments. Each segment is matched against"
              " the given `match` argument."
              ),
        type=str)
    parser.add_argument(
        "destination",
        help=("A path to which the matching file should be copied to."
              " Defaults to `.`"),
        type=str,
        default=os.path.abspath(os.getcwd()))
    parser.add_argument(
        "-v",
        "--verbose",
        dest='verbose',
        help=("Increase logging verbosity to DEBUG"),
        action="store_true")
    parser.add_argument(
        "-s",
        "--use-sudo",
        dest='usesudo',
        help=("Use sudo rights to copy/search on the remote server."),
        action="store_true")

    arguments = parser.parse_args()

    alias = arguments.host

    sshconfigfile = os.path.expanduser('~/.ssh/config')
    if not os.path.exists(sshconfigfile):
        logger.error("Can't find your ssh configuration under "
                     " ~/.ssh/config.")
        sys.exit(1)

    sshconfig = paramiko.SSHConfig()
    sshconfig.parse(open(sshconfigfile, 'r'))
    sshconfighost = sshconfig.lookup(alias)
    hostname = sshconfighost.get('hostname')
    port = int(sshconfighost.get('port', 22))
    user = os.environ['LOGNAME']

    if not hostname:
        logger.warn("Can't find configuration"
                    " for given alias: {alias} in local"
                    " ~/ssh/config. Using it as {hostname}:{port}".format(
                        alias=alias, hostname=alias, port=port)
                    )
        sshconfighost.update(hostname=alias)
    if arguments.verbose:
        logger.setLevel(logging.DEBUG)

    sftpclient = zyklop.ssh.create_fake_sftpclient(sshconfighost,
                                                   arguments.match,
                                                   use_sudo=arguments.usesudo)
    search = zyklop.search.Search(
        '/', arguments.match,
        zyklop.search.ParamikoChildNodeProvider(sftpclient))
    result = search.find()
    if not result:
        logger.info("Can't find {arguments.match} under "
                    "{hostname}:{port}{hostpath}.".format(
                        arguments=arguments,
                        hostpath='/',
                        hostname=hostname,
                        port=port))
        sys.exit(1)

    while result:
        s = raw_input("Use {0}? Y(es)/N(o)/A(bort) ".format(result.path))
        if s.lower() == 'y':
            break
        elif s.lower() == 'a':
            sys.exit(0)
        else:
            search.top = result.path
            result = search.find(children=result.children, visited=result.visited)

    if result:
        localdir = arguments.destination
        cmd = RSYNC_TEMPL.format(
            hostname=hostname,
            remotepath=result.path,
            localdir=localdir).split()
        ssh_cmd = SSH_CMD.format(user=user, port=port)
        cmd.insert(3, ssh_cmd)
        if arguments.usesudo:
            cmd.insert(4, '--rsync-path=sudo rsync')

        logger.info(' '.join(cmd))
        subprocess.call(cmd)
