import os
import os.path


CONFIGFILE = 'config.cfg'
DEFAULTCONFIGDIR = os.path.join(os.environ['HOME'], '.config', 'zyklop')


class Configuration(object):

    def __init__(self, configdir=None, configfile=None):
        self.configdir = configdir and configdir or DEFAULTCONFIGDIR
        self.confgfile = configfile and configfile or CONFIGFILE

    def get_database(self):
        """ Returns the absolute path to the database."""
