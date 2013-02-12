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
from __future__ import print_function
import getpass
import os
import paramiko
import zyklop.command
import zyklop.search


def get_user_pkey(sshconfig):
    """ Returns a list of private keys. If we find an SSH agent, return
        these and try to use them to authenticate. Fallback on
        the identityfile in the sshconfig or ~/.ssh/id_rsa.
    """
    keys = paramiko.Agent().get_keys()
    if not keys:
        keys = []
        privatekeyfile = sshconfig.get('identityfile', '~/.ssh/id_rsa')
        try:
            key = paramiko.RSAKey.from_private_key_file(
                os.path.expanduser(privatekeyfile))
        except paramiko.PasswordRequiredException:
            keypw = getpass.getpass(
                "Password for {0}:".format(privatekeyfile))
            key = paramiko.RSAKey.from_private_key_file(
                filename=os.path.expanduser(privatekeyfile), password=keypw)
        keys.append(key)
    return keys


def create_fake_sftpclient(sshconfig, pattern, **kw):
    """ Creates a new fake sftpclient which supports 'listdir' only. The
        client uses a paramiko.SSHClient for executing a locate on the
        remote system. This is parsed into a tree and can than be used
        for traversing.
    """
    hostname = sshconfig.get('hostname')
    port = int(sshconfig.get('port', 22))
    user = zyklop.command.get_username(sshconfig)
    mykeys = get_user_pkey(sshconfig)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for key in mykeys:
        try:
            client.connect(hostname=hostname,
                           port=port,
                           username=user,
                           pkey=key)
            transport = client.get_transport()
            if transport.is_authenticated:
                break
        except paramiko.SSHException:
            continue
    client.set_log_channel(zyklop.command.logger.name)
    return FakeSFTPClient(client, pattern, **kw)


class FakeSFTPClient(object):
    """ SFTPClient which only implements the listdir method. The listdir
        method supports sudo access and uses a Treenode instance for
        returning it's childrens.
    """
    locate_templ = '{sudo} locate -l 500 -r {pattern}'

    def __init__(self, sshclient, pattern, use_sudo=False):
        self.sshclient = sshclient
        self.tree = self._create_tree(pattern, use_sudo)

    def _create_tree(self, pattern, use_sudo):
        """
        Issues the remote locate command and traverses the returned
        paths into a tree structure.

        TODO: Note to self: I'm not sure if the tree provides any
        benefit here really.
        """
        sudo = use_sudo and 'sudo' or ''
        locatecmd = self.locate_templ.format(sudo=sudo, pattern=pattern)
        locatecmd = locatecmd.strip()
        zyklop.command.logger.debug('Remote: {0}'.format(locatecmd))

        stdin, stdout, stderr = self.sshclient.exec_command(locatecmd)
        error = stderr.read()
        if error:
            raise OSError(
                "An error occured during initialisation: {error}".format(
                    error=error))

        paths = stdout.readlines()
        zyklop.command.logger.debug('Found: {0}'.format(paths))

        tree = zyklop.search.TreeNode()
        for path in paths:
            path = path.strip()
            tree.traverse_path(path)
        return tree

    def listdir(self, abspath):
        segms = abspath.split('/')[1:]
        segms.reverse()
        node = self.tree

        while (segms):
            try:
                node = node[segms.pop()]
            except KeyError:
                break

        children = node.children
        return [zyklop.search.absolute_path(child) for child in children]
