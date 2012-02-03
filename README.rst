==========
 Zyklop ◎
==========

This program is a wrapper around rsync. It should help you:

    * if you need to sync files from remote server frequently
    * No need to keep the location of the file in your mind. It finds
      them for you.

Example Use Case
================

Suppose on server named myserver.foobar.com you have a big file you'd
like to sync. So what you have is:

    Hostname: myserver.foobar.com
    Alias: myserver (Entry in your ~/.ssh/config)
    Correct Path to the file: /opt/big/deployment/foo/bar/myfileordirectorytocopy

To sync now the `myfileordirectorytocopy` from the server, you would
invoke zyklop like:

    $ zyklop myserver myfileordirectory

The second argument can be a regular expression to determine the match.

Use *-v* to see what's happening.

Motivation
==========

I'm dealing with Zope servers most of my time. Some of them have a
*huge* Data.fs - an object oriented database. I do have in 99% of the
cases an older version of the clients database on my PC. Copying the
whole database will take me ages. Using rsync and simply downloading a
binary patch makes updating my local database a quick thing.

To summarize, with zyklop I'd like to address two things:

    1. Downloading large ZODBs takes a long time and
       bandwith. I simply don't want to wait that long.
    2. Most of the time I can not remember the exact path where the item
       to copy is on the remote server.


Not supported ATM
=================

    * Commands are executed with user rights on the server. No sudo
      supported.


Requirements
==============

    * Python >= 2.6 (Python >= 2.7 for tests)
    * rsync installed
    * locate installed with up-to-date database on the remote system


Use --help to see full list of commands.
