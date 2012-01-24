========
 Zyklop
========

This program is a wrapper around rsync. It should help you:

    * sync files from remote servers
    * help you finding those files, thus no need to provide exact paths
      from *where* you sync.

How to Use
==========

Suppose on server named myserver.foobar.com you have a big file you'd
like to sync. So what you have is:

    Hostname: myserver.foobar.com
    Alias: myserver (Entry in your ~/.ssh/config)
    Correct Path to the file: /opt/big/deployment/foo/bar/myfileordirectorytocopy

To sync now the `myfileordirectorytocopy` from the server, you would
invoke zyklop like:

    $ zyklop myserver /opt/bigdeployment myfileordirectory

The second argument is were to start the search and the last parameter
can be a regular expression to determine the match.

Use *-v* to see what's happening.

Motivation
==========

During work, I'll need to sometimes replicate the database contents from
clients servers and basically download their database. I identified two
things:

    1. Downloading sometimes GB big ZODBs takes a long time and
       bandwith. I simply don't want to wait that long.
    2. Most of the time I can not remember the exact path where the item
       to copy is.

Not supported ATM
=================

    * Commands are executed with user rights on the server. No sudo
      supported.

    * Search can perform poor in a big search space.


TODO
====

    * Finding a better heuristic to improve search performance

    * Better command line. Better would be to use something like
      bin/zyklop host:/path match

Requirements
==============

    * Python >= 2.6 (Python >= 2.7 for tests)


Use --help to see full list of commands.
