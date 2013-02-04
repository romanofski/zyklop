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
spameggs. We choose not the first database, but the second::

    $ pwd
    /home/roman/projects/plone4/var/filestorage
    $ zyklop spameggs:Data.fs .
    Use /opt/otherbuildout/var/filestorage/Data.fs? Y(es)/N(o)/A(bort) n
    Use /opt/buildout/var/filestorage/Data.fs? Y(es)/N(o)/A(bort) y
    rsync -av -e ssh -l roman -p 522 --partial --progress --compress-level=9 12.112.11.122:/opt/buildout/var/filestorage/Data.fs /home/roman/projects/plone4/var/filestorage

Syncing a directory which ends with blobstorage, and not directories
like blobstorage.old from a remote server::

    $ pwd
    /home/roman/projects/plone4/var/blobstorage
    $ zyklop spameggs:blobstorage$ .
    Use /opt/buildout/var/blobstorage? Y(es)/N(o)/A(bort) y
    rsync -av -e ssh -l roman -p 522 --partial --progress --compress-level=9 12.112.11.122:/opt/buildout/var/blobstorage /home/roman/projects/plone4/var/

Use an **absolute path** if you know exactly where to copy from::

    $ zyklop spameggs:/tmp/Data.fs .
    Use /tmp/blobstorage? Y(es)/N(o)/A(bort) y
    rsync -av -e ssh -l roman -p 522 --partial --progress --compress-level=9 12.112.11.122:/tmp/Data.fs /home/roman/projects/plone4/var/

Syncing a directory which needs higher privileges. We use the ``-s``
argument::

    $ zyklop -s spameggs:blobstorage$ .
    Use /opt/buildout/var/blobstorage? Y(es)/N(o)/A(bort) y
    rsync -av -e ssh -l roman -p 522 --rsync-path=sudo rsync --partial --progress --compress-level=9 12.112.11.122:/opt/buildout/var/blobstorage /home/roman/projects/plone4/var/

Known Problems
--------------

I've started zyklop and the command just hangs and seems to be doing
nothing.
    This can be caused by paramiko and a not sufficient SSH setup. Make
    sure you can login without problems by simply issuing a::

        ssh myhost

    If that does not solve your problem, try to provide an absolute path
    from the source. Sometimes users don't have many privileges on the
    remote server and the paramiko just waits for the output of a remote
    command::

        zyklop myhost:/path/to/file .

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

    * tty support: sometimes needed if SSH is configured to only allow
      tty's to connect.
    * Don't hang if only password auth is configured for SSH

Development
===========

If you're interested in hacking, clone zyklop on github:

     https://github.com/romanofski/zyklop
