This is an educational/private project only.

This program can be used to sync (hopefully) large files.

Motivation
==========

During work, I'll need to sometimes replicate the database contents from
clients servers and basically download their database. I identified two
things:

    1. Downloading sometimes GB big ZODBs takes a long time and
       bandwith. I simply don't want to wait that long.
    2. Most of the time I can not remember the exact path where the item
       to copy is.

Requirements
==============

    * Python >= 2.6 (Python >= 2.7 for tests)

Sync
====

I've implemented the sync command to be used to synchronize directories
from servers which are usually huge. It uses currently a breadth-first
search alorithm to find the wanted directory.

Use --help to see full list of commands.
