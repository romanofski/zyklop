# Copyright (C) 2012, Roman Joost <roman@bromeco.de>
#
# Kudos to Wolfgang Schnerring from gocept re testlayer setup.
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
import os.path
import threading
import twisted.conch.checkers
import twisted.conch.ssh.connection
import twisted.conch.ssh.factory
import twisted.conch.ssh.keys
import twisted.conch.ssh.userauth
import twisted.conch.unix
import twisted.cred


PUBLIC_KEY = os.path.join(os.path.dirname(__file__), 'data', 'id_rsa.pub')
PRIVATE_KEY = os.path.join(os.path.dirname(__file__), 'data', 'id_rsa')


class UnixSSHdFactory(twisted.conch.ssh.factory.SSHFactory):
    publicKeys = {
        'ssh-rsa': twisted.conch.ssh.keys.Key.fromFile(filename=PUBLIC_KEY)
    }
    privateKeys = {
        'ssh-rsa': twisted.conch.ssh.keys.Key.fromFile(filename=PRIVATE_KEY)
    }
    services = {
        'ssh-userauth': twisted.conch.ssh.userauth.SSHUserAuthServer,
        'ssh-connection': twisted.conch.ssh.connection.SSHConnection
    }


class ThreadedTwistedReactor(object):
    """ Wrapper class to run the twisted reactor in another thread for
        tests to run against.
    """
    port = 5022
    run = True

    def run_until_shutdown(self):
        portal = twisted.cred.portal.Portal(
            twisted.conch.unix.UnixSSHRealm())
        portal.registerChecker(
            twisted.conch.checkers.SSHPublicKeyDatabase())
        UnixSSHdFactory.portal = portal

        twisted.internet.reactor.listenTCP(self.port, UnixSSHdFactory())
        twisted.internet.reactor.run(
            installSignalHandlers=0)

    def shutdown(self):
        twisted.internet.reactor.stop()


class SSHServerLayer(object):
    """ Testlayer which sets up a twisted.conch SSHServer in a separate
        thread to run ssh tests against.
    """

    def __init__(self, *bases):
        self.__bases__ = bases
        if self.__bases__:
            base = bases[0]
            self.__name__ = '(%s.%s)' % (base.__module__, base.__name__)
        else:
            self.__name__ = self.__class__.__name__

    def setUp(self):
        self.treactor = ThreadedTwistedReactor()
        self.reactor_thread = threading.Thread(
            target=self.treactor.run_until_shutdown)
        self.reactor_thread.daemon = True
        self.reactor_thread.start()

    def tearDown(self):
        self.treactor.shutdown()
        self.reactor_thread.join(timeout=1.25)


sshserverlayer = SSHServerLayer()
