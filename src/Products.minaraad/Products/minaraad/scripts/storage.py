import ZODB.utils
import logging
import os
import sys
import tempfile
import time
import ZODB.blob.FilesystemHelper
from ZODB.POSException import POSKeyError
from ZODB.utils import u64
from relstorage.blobhelper import is_blob_record
from relstorage.storage import RelStorage

log = logging.getLogger("minaraad-relstorage")


# First idea: storage only for blobs.  Untested, but something like this:

class BlobOnlyStorage(RelStorage):

    def downloadBlobsFrom(self, other):
        # adapted from RelStorage.copyTransactionsFrom
        if self.blobhelper is None:
            log.error("BlobOnlyStorage has no blobhelper!")
            sys.exit(1)
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
                    dir=self.blobhelper.temporaryDirectory())
                os.close(fd)
                target = open(name, 'wb')
                ZODB.utils.cp(blobfile, target)
                blobfile.close()
                target.close()
                cursor = self._store_cursor
                self.blobhelper.restoreBlob(cursor, record.oid, record.tid, name)

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
                     u64(trans.tid), num_txn_records, rate_str,
                     num_blobs, total_num_blobs,
                     txnum, num_txns, pct_complete)

        elapsed = time.time() - begin_time
        log.info(
            "%d blobs successfully downloaded from all %d transactions in %4.1f minutes.",
            total_num_blobs, txnum, elapsed / 60.0)


# Second idea: create our own blobhelper.

blobhelper = None


def downloadBlobsFrom(other):
    # adapted from RelStorage.copyTransactionsFrom
    if blobhelper is None:
        log.error("BlobOnlyStorage has no blobhelper!")
        sys.exit(1)
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
                dir=blobhelper.temporaryDirectory())
            os.close(fd)
            target = open(name, 'wb')
            ZODB.utils.cp(blobfile, target)
            blobfile.close()
            target.close()
            # blobhelper.restoreBlob(cursor, record.oid, record.tid, name)
            blobhelper.fshelper.getPathForOID(record.oid, create=True)
            targetname = blobhelper.fshelper.getBlobFilename(record.oid, record.tid)
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
                 u64(trans.tid), num_txn_records, rate_str,
                 num_blobs, total_num_blobs,
                 txnum, num_txns, pct_complete)

    elapsed = time.time() - begin_time
    log.info(
        "%d blobs successfully downloaded from all %d transactions in %4.1f minutes.",
        total_num_blobs, txnum, elapsed / 60.0)


# Third idea: we only need the fshelper.

# fshelper = None
fshelper = ZODB.blob.FilesystemHelper(self.blob_dir)


def downloadBlobsFrom(other):
    # adapted from RelStorage.copyTransactionsFrom
    if fshelper is None:
        log.error("No fshelper defined!")
        sys.exit(1)
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
                 u64(trans.tid), num_txn_records, rate_str,
                 num_blobs, total_num_blobs,
                 txnum, num_txns, pct_complete)

    elapsed = time.time() - begin_time
    log.info(
        "%d blobs successfully downloaded from all %d transactions in %4.1f minutes.",
        total_num_blobs, txnum, elapsed / 60.0)
