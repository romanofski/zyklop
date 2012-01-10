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


def get_user_pkey(sshconfig):
    """ Returns the users private key."""
    privatekeyfile = sshconfig.get('identityfile', '~/.ssh/id_rsa')
    try:
        key = paramiko.RSAKey.from_private_key_file(
            os.path.expanduser(privatekeyfile))
    except paramiko.PasswordRequiredException:
        keypw = getpass.getpass(
            "Password for {0}:".format(privatekeyfile))
        key = paramiko.RSAKey.from_private_key_file(
            filename=os.path.expanduser(privatekeyfile), password=keypw)

    return key


def create_sftpclient(sshconfig):
    hostname = sshconfig.get('hostname')
    port = int(sshconfig.get('port', 22))
    mykey = get_user_pkey(sshconfig)
    user = os.environ['LOGNAME']
    transport = paramiko.Transport((hostname, port))
    transport.connect(username=user, pkey=mykey)
    return paramiko.SFTPClient.from_transport(transport)
