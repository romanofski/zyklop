import fabric.api
import re
import os.path


MAXDEPTH = 4


def search_zope2_buildout():
    find_sandbox('/opt', get_children('/opt'))


def find_sandbox(top, children, visited=None, level=0):
    """ BFS to find a zope sandbox."""
    if level == MAXDEPTH:
        return

    if visited is None:
        visited = []
    else:
        for c in visited:
            children += get_children(c)

    while children:
        child = children.pop()
        if child in visited:
            continue
        if child.endswith('bin/instance'):
            print 'found sandbox: {0} at level: {1}'.format(child, level)
            return
        visited.append(child)

    level += 1
    find_sandbox(top, children, visited, level=level)


def find_sandbox_dfs(top, children, visited=None):
    """ DFS to find a zope sandbox """
    if visited is None:
        visited = []

    while children:
        children.reverse()
        child = children.pop()
        if child in visited:
            continue
        if child.endswith('bin/instance'):
            print 'found sandbox: {0}'.format(child)
            return
        visited.append(child)
        find_sandbox_dfs(top, get_children(child), visited)


def get_children(abspath):
    if not abspath.startswith('/'):
        raise ValueError(
            "abspath parameter needs to be an absolute path: {0}".format(
                abspath))
    children = fabric.api.run("ls {0}".format(abspath))
    return [os.path.join(abspath, c) for c in re.split('\s', children)]
