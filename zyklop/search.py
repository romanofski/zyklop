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
import collections
import logging
import os
import re
import collections


class SearchResult(object):

    def __init__(self, path, level, children=None, visited=None):
        self.path = path
        self.level = level
        self.children = children is not None and children or collections.deque()
        self.visited = visited is not None and visited or []

    def __repr__(self):
        return '<{0} object {1}>'.format(
            self.__class__.__name__, self.path)


class TreeNode(object):
    """ A search tree node"""

    def __init__(self, name="/", parent=None):
        self.name = name == "" and "/" or name
        self.parent = parent
        self.children = []

    def append(self, path):
        """ Appends path to the tree."""
        segms = collections.deque(path.split('/'))

        while (segms):
            nname = segms.popleft()
            node = TreeNode(nname, self)
            if node.name == self.name:
                continue
            self.children.append(node)
            return node.append('/'.join(segms))


class Search(object):

    maxdepth = 10

    def __init__(self, top, regexp, childnodeprovider):
        self.top = top
        self.regexp = re.compile(regexp)
        self.childnodeprovider = childnodeprovider
        self.logger = logging.getLogger('zyklop')

    def find(self, children=None, visited=None, level=0):
        """ Performs a BFS and matches every child with the provided
            regular expression to find the goal node.
        """
        if level == self.maxdepth:
            return []
        if visited is None:
            visited = []

        if not children:
            children = collections.deque(
                self.childnodeprovider.get_children(self.top))

        while children:
            child = children.pop()
            self.logger.debug("Searching {0}.".format(child))
            if child in visited:
                continue
            if self.regexp.search(child):
                visited.append(child)
                return SearchResult(child, level, children, visited)
            visited.append(child)

        self.logger.debug("Extending search space.")
        for c in visited:
            children.extendleft(
                self.childnodeprovider.get_children(c))
            self.logger.debug(
                "By {0} nodes".format(
                    len(children)))

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
        raise NotImplementedError("Must be implemented in sublcasses.")


class ParamikoChildNodeProvider(DirectoryChildNodeProvider):

    def __init__(self, sftpclient):
        self.sftpclient = sftpclient

    def _get_children_helper(self, abspath):
        try:
            result = [os.path.join(abspath, c) for c in\
                      self.sftpclient.listdir(abspath)]
        except IOError:
            result = []

        return result
