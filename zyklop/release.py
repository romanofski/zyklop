#!/home/roman/tools/python2.6/bin/python
import fabric.api
import fabric.context_managers
import ConfigParser as configparser
import optparse
import os.path
import sys


def zopestatus(path):
    with fabric.context_managers.cd(path):
        fabric.api.run('bin/instance status')


def main():
    cp = configparser.ConfigParser()
    if not os.path.exists('config.cfg'):
        print('Please create a config file: config.cfg')
        sys.exit(1)
    cp.read('config.cfg')
    hosts = cp.sections()

    parser = optparse.OptionParser()
    parser.add_option('-o', '--host', dest='host',
                      help='Host to run command')

    (options, args) = parser.parse_args()
    if options.host not in hosts:
        parser.error("Invalid host specified. Choose between:\n\n\t{0}".format(
            '\n\t'.join(hosts)))
    path = cp.get(options.host, 'path')
    zopestatus(path)


if __name__ == '__main__':
    main()
