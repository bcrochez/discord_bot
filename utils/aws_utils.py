import os
import threading
import errno
import logging

import boto3
import utils.utils

logger = utils.utils.get_logger('aws', logging.DEBUG)

S3_BUCKET = os.environ.get('S3_BUCKET')
AWS_URL = 'http://s3.amazonaws.com/'

TMP_PATH = '/tmp'


class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            logger.debug("%s --> %s bytes transferred", self._filename, self._seen_so_far)


# Get the service client
s3 = boto3.client('s3')

try:
    os.makedirs(TMP_PATH)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise


def download_file(filename):
    tmp_filename = TMP_PATH+'/'+filename
    logger.debug('Trying to download %s to %s from bucket %s', filename, tmp_filename, S3_BUCKET)
    s3.download_file(S3_BUCKET, filename, tmp_filename,
                     Callback=ProgressPercentage(tmp_filename))
    logger.debug('%s downloaded', filename)
