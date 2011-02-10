import fabric.api
import re
import optparse
import os.path


class Search(object):

    maxdepth = 4

    def __init__(self, top, regexp):
        self.top = top
        self.regexp = re.compile(regexp)

    def find(self, children, visited=None, level=0):
        """ BFS to find a zope sandbox."""
        if level == self.maxdepth:
            return

        if visited is None:
            visited = []
        else:
            for c in visited:
                children += self.get_children(c)

        while children:
            child = children.pop()
            if child in visited:
                continue
            if self.regexp.search(child):
                return (child, level)
            visited.append(child)

        level += 1
        return self.find(children, visited, level=level)

    def get_children(self, abspath):
        if not abspath.startswith('/'):
            raise ValueError(
                "abspath parameter needs to be an absolute path: {0}".format(
                    abspath))
        return self._get_children_helper(abspath)

    def _get_children_helper(self, abspath):
        """ Helper function which returns a list of children. """
        raise NotImplemented("Must be implemented in sublcasses.")


class FabricSearch(Search):

    def _get_children_helper(self, abspath):
        children = fabric.api.run("ls {0}".format(abspath))
        return [os.path.join(abspath, c) for c in re.split('\s', children)]


def search_for_zope():
    parser = optparse.OptionParser()
    parser.add_option(
        "-m", "--match", dest="match",
        help=("A match string the search is looking for. This can be a"
              "path, e.g: bin/instace"),
        type="string",
        default="bin/instance")
    parser.add_option(
        "-p", "--path", dest="path",
        help=("A path in the remote filesystem from where to start the"
              "search. Don't start with the root!"
              " e.g.: /opt"),
        type="string")
    parser.add_option(
        "-s", "--server", dest="server",
        help=("A host to perform the search on."),
        type="string")

    (options, args) = parser.parse_args()
    if not options.path or options.path == '/':
        parser.error(
            "Ehrm - where do you want to search today?")
    if not options.server:
        parser.error(
            "Need a host to connect to. Specify with -s or --server")
    else:
        fabric.api.env.host_string = options.server
    search = FabricSearch(options.path, options.match)
    path, level = search.find(search.get_children(search.top))
    print "Found {0} at level {1}".format(path, level)
