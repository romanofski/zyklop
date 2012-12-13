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
import shlex
import subprocess
import sys
import zyklop.search
import zyklop.ssh


SSH_CMD = 'ssh -l {user} -p {port}'
RSYNC_TEMPL = ('rsync -av -e '
               '-P --compress-level=9 '
               '{hostname}:"{remotepath}" {localdir}')


logger = logging.getLogger('zyklop')
stdout = logging.StreamHandler(sys.stdout)
stdout.setFormatter(logging.Formatter())
logger.addHandler(stdout)
logger.setLevel(logging.INFO)


def get_command(sudo=False, **kw):
    """ Formats the template string and returns subprocess compatible
        command.
    """
    remotepath = kw.get('remotepath')
    cmd = RSYNC_TEMPL.format(**kw)
    ssh_cmd = SSH_CMD.format(**kw)
    cmd = shlex.split(cmd)
    cmd.insert(3, ssh_cmd)
    if sudo:
        cmd.insert(4, '--rsync-path=sudo rsync')
    return cmd


def search_for_remote_path(sshconfighost, match, usesudo):
    """ Depending on the given match, it performs a search on the remote
        server for a match and returns all absolute paths which match.

    ..  note:: Currently only path segments match :(
    ..  note:: If the match is an absolute path, the result will be one
               item which is the given match.

    :param sshconfighost: str - host to connect to
    :param match: str (can be regular expression)
    :param usesudo: boolean. If sudo should be used to find a remote
                    path.
    :rtype: iterable
    """
    if match.startswith('/'):
        result = [zyklop.search.SearchResult(match, 0)]
    else:
        sftpclient = zyklop.ssh.create_fake_sftpclient(
            sshconfighost,
            match,
            use_sudo=usesudo)
        search = zyklop.search.Search(
            '/', match,
            zyklop.search.ParamikoChildNodeProvider(sftpclient))
        result = search.findall()
    return result


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
        "source",
        help=("A sourcehost:path string. The source host has to be a valid"
              " host or ssh alias for a host. The path either an absolute path"
              " or regular expression for a path segment. Zyklop"
              " connects to the server and finds an absolute path for you."
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

    alias, match = arguments.source.split(':', 1)

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

    results = search_for_remote_path(
        sshconfighost, match, arguments.usesudo)
    if not results:
        logger.info("Can't find {match} under "
                    "{hostname}:{port}{hostpath}.".format(
                        arguments=arguments,
                        match=match,
                        hostpath='/',
                        hostname=hostname,
                        port=port))
        sys.exit(1)

    for result in results:
        s = raw_input("Use {0}? (Y)es/(N)o/(A)bort ".format(result.path))
        if s.lower() == 'y':
            localdir = arguments.destination
            cmd = get_command(arguments.usesudo, **dict(
                hostname=hostname,
                remotepath=result.path,
                localdir=localdir,
                user=user,
                port=port)
                )
            logger.info(' '.join(cmd))
            subprocess.call(cmd)
            break
        elif s.lower() in ['a', 'q']:
            sys.exit(0)

