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


First Steps
===========

If you are new to ssh, setup an ssh configuration first. If you are
dealing with a lot of servers, giving them an alias makes them easier to
remember and you don't have to type as much.

    #. Create an ssh configuration in your SSH home, e.g.::

        vim ~/.ssh/config

       You can use the following example as a starter::

        Host spameggs
        Hostname  12.112.11.122
        Compression yes
        CompressionLevel 9
        User guido

       but be sure to check the `documentation
       <https://duckduckgo.com/?q=ssh+config+documentation&t=canonical>`_
       or the man page (5) for `ssh_config`

    #. Make the config only readable for the owner::

        chmod 600 ~/.ssh/config

    #. Test if you can login to your configured host using only your
       alias::

        ssh spameggs

Examples
========

    #. Syncing ZODB from remote server configured in ``~/.ssh/config``
       as spameggs. We choose not the first database, but the second::

        $ zyklop spameggs:Data.fs .
        Use /opt/otherbuildout/var/filestorage/Data.fs? Y(es)/N(o)/A(bort) n
        Use /opt/buildout/var/filestorage/Data.fs? Y(es)/N(o)/A(bort) y

    #. Syncing a directory providing a path segment::

        $ zyklop spameggs:buildout/var/filestorage$ .

    #. Syncing a directory which ends with `blobstorage``, excluding any
       other `blobstorage` directories with postfixes in the name (e.g.
       `blobstorage.old`)::

        $ zyklop spameggs:blobstorage$ .

    #. Use an **absolute path** if you know exactly where to copy from::

        $ zyklop spameggs:/tmp/Data.fs .

    #. Syncing a directory which needs higher privileges. We use the
       ``-s`` argument::

        $ zyklop -s spameggs:blobstorage$ .

    #. **Dry run** prints out all found remote paths and just exits::

        $ zyklop -d spameggs:blobstorage$ .
        /opt/otherbuildout/var/blobstorage
        /opt/otherbuildout/var/blobstorage.old
        /opt/buildout/var/blobstorag

    #. Sync the first result zyklop finds automatically **without
       prompting**::

        $ zyklop -y spameggs:blobstorage$ .


Known Problems
--------------

Zyklop just hangs
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
