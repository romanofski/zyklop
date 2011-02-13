import fabric.api
import re
import optparse
import os.path


class SearchResult(object):

    def __init__(self, path, level):
        self.path = path
        self.level = level


class Search(object):

    maxdepth = 4

    def __init__(self, top, regexp):
        self.top = top
        self.regexp = re.compile(regexp)

    def find(self, children=None, visited=None, level=0):
        """ BFS to find a zope sandbox."""
        if level == self.maxdepth:
            return []
        if not children:
            children = self.get_children(self.top)

        if visited is None:
            visited = []
        else:
            for c in visited:
                children += self.get_children(c)

        found = []
        while children:
            child = children.pop()
            if child in visited:
                continue
            if self.regexp.search(child):
                found.append(SearchResult(child, level))
            visited.append(child)

        level += 1
        result = self.find(children, visited, level=level)
        if result is not None:
            found += result
        return found

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
    path, level = search.find()
    print "Found {0} at level {1}".format(path, level)
