#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2015 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""RelStorage Blob download utility.

Use case:

You have a RelStorage without shared blob directory, so with the blobs
stored in the relational database, and want to move to RelStorage WITH
shared blob directory.

One way to do that, would be to download the blobs into a new
directory and then start using that as the shared blob directory.

This script does that.  It also, optionally, removes the blob_chunks
and large objects from the database.  Use the --delete-blobs option
for this.

An alternative for the --delete-blobs option, at least on Postgres, is:

1. In a psql prompt, type: `TRUNCATE blob_chunk;` to empty this table.
   This is near instantaneous.

2. As postgres user (database admin) run `vacuumlo databasename` to
   cleanup the large objects.  This can take a few minutes.

Note: a blob may be stored in multiple blob_chunks if it is very
large.  Restoring and deleting this is untested, so currently the
script stops when it encounters such a blob.

Sample config file:

<relstorage source>
  blob-dir /some/dir/var/blobcache
  shared-blob-dir false
  <postgresql>
    dsn dbname='client_plone4' user='client' host='localhost' port='5432' password='secret'
  </postgresql>
</relstorage>

new_blob_dir must be the path to a directory that does not exist yet.
Otherwise the script will quit immediately.

"""  # noqa

import ZConfig
import ZODB.blob
import ZODB.utils
import logging
import optparse
import os
import shutil
import sys
import tempfile
import time
from StringIO import StringIO
from ZODB import POSException
from ZODB.utils import p64
from relstorage.iter import fetchmany

schema_xml = """
<schema>
  <import package="ZODB"/>
  <import package="relstorage"/>
  <section type="ZODB.storage" name="source" attribute="source"
    required="yes" />
</schema>
"""

log = logging.getLogger("blobdownload")


all_blobs_stmt = """
    SELECT zoid, tid, chunk_num
    FROM blob_chunk
    ORDER BY chunk_num
    """


def delete_blob_chunks(cursor, oids, options):
    """Delete the blob_chunks for specified object ids.

    We use a bit of batching, but not sure if that makes sense.  If
    someone wanted to add commit locks, plus maybe a pause between
    commits, this could be a good spot.  But the delete_blobs option
    should only be used when no one else is using the database anyway:
    you delete blobs because your current database uses a non-shared
    blobcache and you are about to switch to a shared blobstorage
    directory.  You should not be using the database at that point.

    The batching does give more sense of progress, which is good for
    your heart.
    """
    oids = list(oids)
    total = len(oids)
    if options.dry_run:
        log.info("Dry-run selected. Would delete %d blob_chunks from "
                 "the database." % total)
    else:
        log.info("Deleting %d blob_chunks from the database.", total)
    batch = 100
    log.info("Using batch size of %d.", batch)
    done = 0
    while oids:
        current_batch = oids[:batch]
        current_batch_len = len(current_batch)
        oid_list = ','.join(str(oid) for oid in current_batch)
        del oids[:batch]
        if options.dry_run:
            stmt = "SELECT zoid FROM blob_chunk WHERE zoid IN (%s)" % (
                oid_list)
            cursor.execute(stmt)
            # Fetch them to see that it works.
            count = 0
            for oid in fetchmany(cursor):
                count += 1
                pass
            done += count
            pct_complete = '%1.2f%%' % (done * 100.0 / total)
            log.info("Would delete %4d blob chunks. | %5d (%d total) | %7s",
                     count, done, total, pct_complete)
        else:
            stmt = "DELETE FROM blob_chunk WHERE zoid IN (%s)" % (oid_list)
            cursor.execute(stmt)
            done += current_batch_len
            pct_complete = '%1.2f%%' % (done * 100.0 / total)
            log.info("Deleted %4d oids. | %5d (%d total) | %7s",
                     current_batch_len, done, total, pct_complete)


def download_blobs(other, blob_dir, options):
    # adapted from RelStorage.copyTransactionsFrom
    fshelper = ZODB.blob.FilesystemHelper(blob_dir)
    fshelper.create()
    fshelper.checkSecure()
    if options.delete_blobs and other._is_read_only:
        msg = "ERROR: cannot delete blobs: source storage is readonly."
        sys.exit(msg)
    begin_time = time.time()
    stmt = all_blobs_stmt
    log.info("Counting the blobs.")
    total_blobs = 0
    other._lock_acquire()
    try:
        other._before_load()
        cursor = other._load_cursor
        cursor.execute(stmt)
        for zoid, tid, chunk_num in cursor.fetchall():
            total_blobs += 1
            if chunk_num > 0:
                msg = ("ERROR: zoid %s in tid %s has more than one chunk. "
                       "This is untested, so for safety this is "
                       "not supported yet. Stopping execution. "
                       "No blobs were downloaded or deleted." % (zoid, tid))
                sys.exit(msg)
    finally:
        other._lock_release()

    log.info("There are %d blobs.", total_blobs)
    num_blobs = 0
    oids_to_delete = set()
    if options.limit > -1:
        log.info("Limiting download to at most %d blobs.", options.limit)
        stmt += " LIMIT %d" % options.limit
        log.info("Downloading %d blobs.", min(options.limit, total_blobs))
    else:
        log.info("Downloading %d blobs.", total_blobs)
    other._lock_acquire()
    try:
        other._before_load()
        cursor = other._load_cursor
        cursor.execute(stmt)
        for zoid, tid, chunk_num in cursor.fetchall():
            if options.dry_run:
                oids_to_delete.add(zoid)
                num_blobs += 1
                continue
            # Note: this might not work well when there is another row in
            # blob_chunk, with a different chunk_num.  That can happen for
            # really large files, 2GB on Postgres.

            # The zoids and tids in the result row are 64-bit long
            # integers.  We need to pack them into 8-byte strings.
            packed_zoid = p64(zoid)
            packed_tid = p64(tid)
            try:
                blobfile = other.openCommittedBlobFile(
                    packed_zoid, packed_tid)
            except POSException.POSKeyError:
                log.warn("POSKeyError on zoid %s, tid %s", zoid, tid)
                continue
            if blobfile is None:
                continue
            num_blobs += 1
            fd, name = tempfile.mkstemp(
                suffix='.tmp',
                dir=fshelper.temp_dir)
            os.close(fd)
            target = open(name, 'wb')
            ZODB.utils.cp(blobfile, target)
            blobfile.close()
            target.close()
            fshelper.getPathForOID(packed_zoid, create=True)
            targetname = fshelper.getBlobFilename(packed_zoid, packed_tid)
            ZODB.blob.rename_or_copy_blob(name, targetname)
            oids_to_delete.add(zoid)

            pct_complete = '%1.2f%%' % (num_blobs * 100.0 / total_blobs)
            log.info("Downloaded zoid %d, tid %d | %5d blobs (%d total) | %7s",
                     zoid, tid, num_blobs, total_blobs, pct_complete)

        log.info("Done downloading to %s", blob_dir)
    finally:
        other._lock_release()
    # At the end, remove the blob chunks that were correctly downloaded.
    if not options.delete_blobs:
        log.info("--delete-blobs option not used. "
                 "Keeping %d blob_chunks in the database." %
                 len(oids_to_delete))
    else:
        other._lock_acquire()
        try:
            conn, cursor = other._adapter.connmanager.open()
            other._adapter.locker.hold_commit_lock(cursor)
            delete_blob_chunks(cursor, oids_to_delete, options)
            conn.commit()
            other._adapter.locker.release_commit_lock(cursor)
        finally:
            other._lock_release()

    elapsed = time.time() - begin_time
    log.info(
        "%d (out of %d) blobs successfully downloaded in %4.1f minutes.",
        num_blobs, total_blobs, elapsed / 60.0)
    if total_blobs > num_blobs:
        if options.limit > -1 and options.limit == num_blobs:
            log.info("Blob download was limited to %d, and that number "
                     "was downloaded.", options.limit)
        else:
            log.warn("%d blobs were not downloaded. There may have been "
                     "problems. Problematic blobs will not have been deleted.",
                     total_blobs - num_blobs)


class SaneDescriptionFormatter(optparse.IndentedHelpFormatter):

    def format_description(self, description):
        # No, we do not want to wrap the lines, thank you...
        return description


def main(argv=sys.argv):
    parser = optparse.OptionParser(
        description=__doc__,
        usage="%prog [options] config_file new_blob_dir",
        formatter=SaneDescriptionFormatter())
    parser.add_option(
        "--dry-run", dest="dry_run", action="store_true",
        help="Attempt to open the storage, then explain what would be done")
    parser.add_option(
        "--clear", dest="clear", action="store_true",
        help="Delete the destination blob directory before "
             "downloading, to force a clean download.")
    parser.add_option(
        "--delete-blobs", dest="delete_blobs", action="store_true",
        help="Delete the blobs from the source database (blob_chunk table). "
             "Any blobs for which the download fails, will be left. "
             "This is done at the end when all is downloaded.")
    parser.add_option(
        "--limit", dest="limit", action="store", type="int",
        help="Download and/or delete at most this number of blobs. "
             "Default: no limit (technically: -1).")
    parser.set_defaults(dry_run=False, clear=False,
                        delete_blobs=False, limit=-1)
    options, args = parser.parse_args(argv[1:])

    if len(args) != 2:
        parser.error("The name of a configuration file and new blob dir "
                     "is required.")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s")
    if options.dry_run:
        log.info("Dry-run selected.")

    blob_dir = args[1]
    if os.path.exists(blob_dir):
        if options.clear:
            if options.dry_run:
                log.info("Dry-run selected. Would delete %s ...", blob_dir)
            else:
                log.info("Deleting %s ...", blob_dir)
                shutil.rmtree(blob_dir)
        else:
            log.info("Adding to existing blob dir %s", blob_dir)

    schema = ZConfig.loadSchemaFile(StringIO(schema_xml))
    config, handler = ZConfig.loadConfig(schema, args[0])
    source = config.source.open()
    log.info("Storage opened successfully.")

    download_blobs(source, blob_dir, options)
    source.close()


if __name__ == '__main__':
    main()
