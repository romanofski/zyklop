==========
 Zyklop ◎
==========

This program is a wrapper around rsync. It will help you:

    * if you need to sync files from remote server frequently
    * No need to keep the location of the file in your mind. It finds
      them for you.

Requirements
==============

    * Python >= 2.6 (Python >= 2.7 for tests)
    * rsync installed
    * locate installed with up-to-date database on the remote system

SSH Configuration
-----------------

Make sure you have an SSH configuration file in your ``$HOME``
directory. This tends to be very useful, as it keeps all necessary
logins and ssh server access configurations, e.g.::

    Host spameggs
    Hostname  12.112.11.122
    Compression yes
    CompressionLevel 9
    User guido

    Host example2
    HostName example2.examples.com
    User johndoe
    Port 22

Examples
========

..  note::
    Reusing server definitions from SSH Configuration.

Syncing ZODB from remote server configured in ``~/.ssh/config`` as
spameggs::

    $ zyklop spameggs Data.fs

Motivation
==========

I'm dealing with Zope servers most of my time. Some of them have a
*huge* Data.fs - an object oriented database. I do have in 99% of the
cases an older version of the clients database on my PC. Copying the
whole database will take me ages. Using rsync and simply downloading a
binary patch makes updating my local database a quick thing.

To summarize, with zyklop I'd like to address two things:

    1. Downloading large ZODBs takes a long time and
       bandwidth. I simply don't want to wait that long and download that
       much.
    2. Most of the time I can not remember the exact path where the item
       to copy is on the remote server.


TODO
====

    * sudo support on the remote server
    * support for copying if SSH expects a terminal
