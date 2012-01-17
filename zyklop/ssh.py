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
import logging
import os
import paramiko
import sys


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


def create_sftpclient(sshconfig):
    """ Creates a new sftpclient which is authenticated with the host.
        It tries to authenticate via public key given by the ssh agent of
        sshconfig file. If that fails, no sftpclient is created and the
        factory exits with sys.exit(1)
    """
    logger = logging.getLogger('zyklop')
    hostname = sshconfig.get('hostname')
    port = int(sshconfig.get('port', 22))
    mykeys = get_user_pkey(sshconfig)
    user = os.environ['LOGNAME']
    transport = paramiko.Transport((hostname, port))
    transport.start_client()

    for key in mykeys:
        try:
            transport.auth_publickey(username=user, key=key)
        except paramiko.SSHException, e:
            # XXX better tell the user?
            pass

    if not transport.is_authenticated():
        logger.warn("Key Authentication failed.")
        sys.exit(1)

    return paramiko.SFTPClient.from_transport(transport)
