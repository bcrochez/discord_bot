import os
import threading
import logging

import boto3
import utils.utils as utils
import utils.constants as const

logger = utils.get_logger('aws', logging.DEBUG)

S3_BUCKET = os.environ.get('S3_BUCKET')


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

utils.make_dir(const.TMP_PATH)


def download_file(filename):
    tmp_filename = const.TMP_PATH+'/'+filename
    utils.make_dir(os.path.dirname(tmp_filename))
    logger.debug('Trying to download %s to %s from bucket %s', filename, tmp_filename, S3_BUCKET)
    s3.download_file(S3_BUCKET, filename, tmp_filename,
                     Callback=ProgressPercentage(tmp_filename))
    logger.debug('%s downloaded', filename)


def upload_file(filename):
    tmp_filename = const.TMP_PATH+'/'+filename
    logger.debug('Trying to upload %s to %s into bucket %s', tmp_filename, filename, S3_BUCKET)
    s3.upload_file(tmp_filename, S3_BUCKET, filename)
    logger.debug('%s uploaded', filename)
