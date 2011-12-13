This is an educational/private project only. I played around with search
algorithms and that's what comes out of it.

Requirements
==============

    * Python >= 2.7

Sync
====

I've implemented the sync command to be used to synchronize directories
from servers which are usually huge.

Use --help to see full list of commands.

Motivation
----------

For example, I need to copy ZODBs
and their blobstorages from the server to be able to debug it and keep
them up to date. Sometimes I can't remember exactly where the
deployments are. Therefore I want a script which simply finds the
storages and copies them to my local sandbox (perhaps syncs them if I
need to do that again).
