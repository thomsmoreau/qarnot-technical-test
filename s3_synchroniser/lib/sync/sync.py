"""Module for synchronizing local files with an S3 bucket."""

import os
import warnings
from datetime import datetime, timezone

from s3_synchroniser.lib.files_manager.files_manager import get_local_files
from s3_synchroniser.lib.logger.logger import get_logger
from s3_synchroniser.lib.s3_manager.s3_manager import S3Manager

LOGGER = get_logger(__name__)


def sync_files_with_s3(s3_manager: S3Manager):
    """Sync files in local path given to the S3 bucket used by the S3 manager passed

    Args:
        s3_manager (S3Manager): S3 manager to use to interact with S3 storage
    """
    # Suppress HeaderParsingError warnings from urllib3
    warnings.filterwarnings("ignore", category=Warning)

    local_files = get_local_files(s3_manager.s3_config.local_path)
    s3_files = s3_manager.get_bucket_files()

    LOGGER.info("Starting synchro with bucket")
    for local_file in local_files:
        if local_file not in s3_files:
            s3_manager.upload_file(local_file, local_file)
            continue
        else:
            # Compare last modified times
            local_mtime = datetime.fromtimestamp(
                os.path.getmtime(local_file), tz=timezone.utc
            )
            s3_mtime = s3_manager.get_object_last_modified(local_file)
            if s3_mtime and local_mtime > s3_mtime:
                LOGGER.info("Updating modified file '%s' in S3", local_file)
                s3_manager.upload_file(local_file, local_file)
            else:
                LOGGER.info("No changes detected for '%s'", local_file)

    for s3_file in s3_files:
        if s3_file not in local_files:
            s3_manager.delete_file(s3_file)
