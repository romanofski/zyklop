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
import os
import os.path
import re
import unittest
import zyklop.search
import zyklop.tests.base


FAKEFSTREE = {'/': dict(
    folder1=dict(
        bin=dict(instance=dict())
    ),
    folder2=dict(
        bin=dict()),
    folder3=dict(),
)
}


class TestWalkFakeFSTree(unittest.TestCase):

    def test_get_children(self):
        cnprov = DummyTreeChildNodeProvider()
        children = cnprov.get_children('/')
        self.assertEquals(['/folder3', '/folder2', '/folder1'], children)

        children = cnprov.get_children('/folder3')
        self.assertEquals([], children)

        children = cnprov.get_children('/folder1/bin')
        self.assertEquals(['/folder1/bin/instance'], children)


class DummyTreeChildNodeProvider(object):

    def get_children(self, path):
        return self.get_children_helper(path, FAKEFSTREE)

    def get_children_helper(self, path, tree):
        def walk(path, tree, visited=None):
            if visited == None:
                visited = []
            segm = path.pop()
            if segm == '':
                segm = '/'
            visited.append(segm)
            if path:
                children = walk(path, tree[segm], visited)
            else:
                children = tree[segm].keys()
            children = [os.path.join(*visited + [x]) for x in children]
            return children

        if path == '/':
            segments = ['']
        else:
            segments = path.split('/')
            segments.reverse()
        return walk(segments, tree)


class TestSearch(unittest.TestCase):
    """ Basic test to test the BFS and DFS searches """

    def test_find(self):
        search = zyklop.search.Search('/', '^.*bin/instance',
                                     DummyTreeChildNodeProvider())
        # we'll use os.listdir to get the children
        found = search.find()
        self.assertTrue(found)
        self.assertTrue(found.path.endswith('folder1/bin/instance'))
        self.assertEquals(found.level, 2)

        search.regexp = re.compile('^.*bin$')
        found = search.find()
        self.assertTrue(found.path.endswith('folder1/bin'))

    def test_noresult(self):
        search = zyklop.search.Search('/', 'foobarnotexist',
                                      DummyTreeChildNodeProvider())
        found = search.find()
        self.assertEquals(found, [])


class TestSearchResult(unittest.TestCase):

    def test__repr__(self):
        sr = zyklop.search.SearchResult('/', 2)
        self.assertEquals('<SearchResult object />', repr(sr))
