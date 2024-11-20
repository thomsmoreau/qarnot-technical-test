from s3_synchroniser.lib.s3_manager.s3_config import get_s3_config
from s3_synchroniser.lib.s3_manager.s3_manager import S3Manager
from s3_synchroniser.lib.sync.sync import sync_files_with_s3

if __name__ == "__main__":
    s3_config = get_s3_config()
    s3_manager = S3Manager(s3_config)
    sync_files_with_s3(s3_manager)
