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
import os
import paramiko


def get_user_pkey():
    """ Returns the users private key."""
    privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
    return paramiko.RSAKey.from_private_key_file(privatekeyfile)


def create_sftpclient(hostname, port=22):
    mykey = get_user_pkey()
    user = os.environ['LOGNAME']
    transport = paramiko.Transport((hostname, port))
    transport.connect(username=user, pkey=mykey)
    return paramiko.SFTPClient.from_transport(transport)
