import os
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

    def __init__(self, top, regexp, childnodeprovider):
        self.top = top
        self.regexp = re.compile(regexp)
        self.childnodeprovider = childnodeprovider

    def find(self, children=None, visited=None, level=0):
        """ BFS to find a zope sandbox."""
        if level == self.maxdepth:
            return []
        if not children:
            children = self.childnodeprovider.get_children(self.top)

        if visited is None:
            visited = []
        else:
            for c in visited:
                children += self.childnodeprovider.get_children(c)

        while children:
            child = children.pop()
            if child in visited:
                continue
            if self.regexp.search(child):
                return SearchResult(child, level)
            visited.append(child)

        level += 1
        return self.find(children, visited, level=level)


class DirectoryChildNodeProvider(object):

    def get_children(self, abspath):
        if not abspath.startswith('/'):
            raise ValueError(
                "abspath parameter needs to be an absolute path: {0}".format(
                    abspath))
        return self._get_children_helper(abspath)

    def _get_children_helper(self, abspath):
        """ Helper function which returns a list of children. """
        raise NotImplemented("Must be implemented in sublcasses.")


class ParamikoChildNodeProvider(DirectoryChildNodeProvider):

    def __init__(self, sftpclient):
        self.sftpclient = sftpclient

    def _get_children_helper(self, abspath):
        return [os.path.join(abspath, c) for c in\
                self.sftpclient.listdir(abspath)]
