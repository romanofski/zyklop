import argparse
import fabric.api
import zyklop.sshconfig
import zyklop.search


def sync_storages():
    parser = argparse.ArgumentParser(description="Syncs local storages")
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

    arguments = parser.parse_args()
    if not arguments.path or arguments.path == '/':
        parser.error(
            "Ehrm - where do you want to search today?")
    sshconfig = zyklop.sshconfig.SSHConfigParser().parse()
    fabric.api.env.host_string = '{host}:{port}'.format(
        host=sshconfig[arguments.alias].HostName,
        port=sshconfig[arguments.alias].Port)
    search = zyklop.search.FabricSearch(arguments.path, arguments.match)
    results = search.find()
    for i in results:
        print "Found {0} at level {1}".format(i.path, i.level)
