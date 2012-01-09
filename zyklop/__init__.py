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
import sys
import zyklop.rsync
import zyklop.search
import zyklop.ssh


logger = logging.getLogger('zyklop')
stdout = logging.StreamHandler(sys.stdout)
stdout.setFormatter(logging.Formatter())
logger.addHandler(stdout)
logger.setLevel(logging.INFO)


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
    port = int(host.get('port', 22))

    if not hostname:
        parser.error("Can't find configuration"
                     " for given alias: {0} in local ~/ssh/config".format(
                         arguments.alias)
                    )

    search = zyklop.search.Search(
        arguments.path, arguments.match,
        zyklop.search.ParamikoChildNodeProvider(
            zyklop.ssh.create_sftpclient(hostname, port)))
    result = search.find()
    if arguments.dry_run and result:
        logger.info("Found {0}".format(result.path))
        sys.exit(0)

    elif result:
        localdir = os.path.abspath(os.getcwd())
        rsync = zyklop.ssh.SSHRsync(
            zyklop.ssh.create_sftpclient(hostname, port))
        rsync.sync(os.path.join(
            localdir, os.path.basename(result.path)), result.path)
    else:
        logger.info("Can't find {arguments.match} under "
                    "{hostname}:{port}{arguments.path}.".format(
                        arguments=arguments, hostname=hostname, port=port))
        sys.exit(1)
