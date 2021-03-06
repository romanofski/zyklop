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
import zyklop
import zyklop.search
import zyklop.ssh


SSH_CMD = 'ssh -l {user} -p {port}'
RSYNC_TEMPL = ('rsync -av -e '
               '-P --compress-level=9 '
               '{hostname}:"{remotepath}" {localdir}')
ERROR_NO_SSH_CONFIGFILE = ("Can't find your ssh configuration under"
                           " ~/.ssh/config. Please create one and consult"
                           " the man page ssh_config (5)")


logger = logging.getLogger('zyklop')
stdout = logging.StreamHandler(sys.stdout)
stdout.setFormatter(logging.Formatter())
logger.addHandler(stdout)
logger.setLevel(logging.INFO)


def get_username(sshconfig={}):
    """ Returns a string of the username retrieved from the sshconfig.
        Falls back to the `user` of the environment.
    """
    return sshconfig.get('user', os.environ['LOGNAME'])


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


def _setup_commandline_arguments():
    """ Helper method to setup arguments and argument parser. """
    parser = argparse.ArgumentParser(
        description='{name} {version} -- {description}'.format(
            name=zyklop.__name__, version=zyklop.__version__,
            description=zyklop.__description__),
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
        "--version",
        action="version",
        version="{name} {version}".format(
            name=zyklop.__name__, version=zyklop.__version__),)
    parser.add_argument(
        "-d",
        "--dry-run",
        dest='dryrun',
        help=("Selects a dry run, which prints only the found source "
              "path(s). If multiple paths are found, the paths are "
              "newline separated"),
        action="store_true")
    parser.add_argument(
        "-s",
        "--use-sudo",
        dest='usesudo',
        help=("Use sudo rights to copy/search on the remote server."),
        action="store_true")
    parser.add_argument(
        "-y",
        "--assume-yes",
        dest='assumeyes',
        help=("Pick the first found destination path for syncing and "
              "don't prompt the user."),
        action="store_true")
    return parser


def sync():
    """ Entry point which parses given arguments, searches for a
        file/directory to sync on the remote server and passes it on to
        rsync.
    """
    sshconfigfile = os.path.expanduser('~/.ssh/config')
    if not os.path.exists(sshconfigfile):
        logger.error(ERROR_NO_SSH_CONFIGFILE)
        sys.exit(1)

    parser = _setup_commandline_arguments()
    arguments = parser.parse_args()
    alias, match = arguments.source.split(':', 1)
    sshconfig = paramiko.SSHConfig()
    sshconfig.parse(open(sshconfigfile, 'r'))
    sshconfighost = sshconfig.lookup(alias)
    hostname = sshconfighost.get('hostname')
    port = int(sshconfighost.get('port', 22))
    user = get_username(sshconfighost)

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
        # in a dry run mode, we only print all result paths
        if arguments.dryrun:
            logger.info(result.path)
            continue

        # otherwise, keep on looping and ask the user if we should pass
        # the selected path to rsync
        if not arguments.assumeyes:
            s = raw_input("Use {0}? (Y)es/(N)o/(A)bort ".format(result.path))
        else:
            s = 'y'

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
    sys.exit(0)
