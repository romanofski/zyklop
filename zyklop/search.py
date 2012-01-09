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
import logging
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
        self.logger = logging.getLogger('zyklop')

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
            self.logger.debug("Searching {0}.".format(child))
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
        try:
            result = [os.path.join(abspath, c) for c in\
                      self.sftpclient.listdir(abspath)]
        except IOError:
            result = []

        return result
