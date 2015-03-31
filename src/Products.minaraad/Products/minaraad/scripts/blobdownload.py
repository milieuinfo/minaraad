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

Note: this does leave blob_chunks and large objects behind in the
database, which you may want to clean up.  That is, currently, NOT
something that this script will wandle for you.

Usage: blobdownload config_file new_blob_dir

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

"""

import ZConfig
import ZODB.blob
import ZODB.utils
import logging
import optparse
import os
import sys
import tempfile
import time
from StringIO import StringIO
from ZODB.POSException import POSKeyError
from ZODB.utils import u64
from relstorage.blobhelper import is_blob_record

schema_xml = """
<schema>
  <import package="ZODB"/>
  <import package="relstorage"/>
  <section type="ZODB.storage" name="source" attribute="source"
    required="yes" />
</schema>
"""

log = logging.getLogger("blobdownload")


def download_blobs(other, blob_dir):
    # adapted from RelStorage.copyTransactionsFrom
    fshelper = ZODB.blob.FilesystemHelper(blob_dir)
    fshelper.create()
    fshelper.checkSecure()
    begin_time = time.time()
    txnum = 0
    total_size = 0
    log.info("Counting the transactions.")
    num_txns = 0
    for _ in other.iterator():
        num_txns += 1
    log.info("Downloading the blobs.")
    total_num_blobs = 0
    for trans in other.iterator():
        txnum += 1
        num_blobs = 0
        num_txn_records = 0
        for record in trans:
            num_txn_records += 1
            blobfile = None
            if not is_blob_record(record.data):
                continue
            try:
                blobfile = other.openCommittedBlobFile(
                    record.oid, record.tid)
            except POSKeyError:
                continue
            if blobfile is None:
                continue
            fd, name = tempfile.mkstemp(
                suffix='.tmp',
                dir=fshelper.temp_dir)
            os.close(fd)
            target = open(name, 'wb')
            ZODB.utils.cp(blobfile, target)
            blobfile.close()
            target.close()
            fshelper.getPathForOID(record.oid, create=True)
            targetname = fshelper.getBlobFilename(record.oid, record.tid)
            ZODB.blob.rename_or_copy_blob(name, targetname)

            num_blobs += 1
            if record.data:
                total_size += len(record.data)

        pct_complete = '%1.2f%%' % (txnum * 100.0 / num_txns)
        elapsed = time.time() - begin_time
        if elapsed:
            rate = total_size / 1e6 / elapsed
        else:
            rate = 0.0
        rate_str = '%1.3f' % rate
        total_num_blobs += num_blobs
        log.info("Studied tid %d,%5d records | %d blobs (%d total) | %6s MB/s (%6d/%6d,%7s)",
                 u64(trans.tid), num_txn_records,
                 num_blobs, total_num_blobs,
                 rate_str, txnum, num_txns, pct_complete)

    elapsed = time.time() - begin_time
    log.info(
        "%d blobs successfully downloaded from all %d transactions in %4.1f minutes.",
        total_num_blobs, txnum, elapsed / 60.0)


def main(argv=sys.argv):
    parser = optparse.OptionParser(description=__doc__,
        usage="%prog config_file new_blob_dir")
    options, args = parser.parse_args(argv[1:])

    if len(args) != 2:
        parser.error("The name of a configuration file and new blob dir is required.")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s")

    blob_dir = args[1]
    if os.path.exists(blob_dir):
        log.error("Blob dir %s already exists." % blob_dir)
        sys.exit(1)
    schema = ZConfig.loadSchemaFile(StringIO(schema_xml))
    config, handler = ZConfig.loadConfig(schema, args[0])
    source = config.source.open()
    log.info("Storage opened successfully.")

    download_blobs(source, blob_dir)
    source.close()


if __name__ == '__main__':
    main()
