import fabric.api
import fabric.state
import os.path
import re


class SearchResult(object):

    def __init__(self, path, level):
        self.path = path
        self.level = level

    def __repr__(self):
        return '<{0} object {1}>'.format(
            self.__class__.__name__, self.path)


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
        if not found:
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
        fabric.api.env.warn_only = True
        fabric.state.output.running = False
        fabric.state.output.stdout = False
        result = fabric.api.run("ls {0}".format(abspath))
        children = result.failed != True and result or ''
        return [os.path.join(abspath, c) for c in re.split('\s', children)]

