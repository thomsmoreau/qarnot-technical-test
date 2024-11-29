import os
from datetime import timezone

import boto3
import boto3.session
from botocore.exceptions import ClientError

from s3_synchroniser.lib.logger.logger import get_logger
from s3_synchroniser.lib.s3_manager.s3_config import S3Configuration

LOGGER = get_logger(__name__)


class S3Manager:
    """Handles interactions with S3 storages, such as bucket existence and file listing."""

    def __init__(self, s3_config: S3Configuration):
        """
        Initialize S3Manager with connection details.
        """
        self.s3_config = s3_config
        self.s3_client = self._create_s3_client()

    def _create_s3_client(self):
        """
        Create a boto3 client for S3 or MinIO. Private
        """

        s3_client = boto3.client(
            "s3",
            endpoint_url=self.s3_config.endpoint_url,
            aws_access_key_id=self.s3_config.credentials.access_key,
            aws_secret_access_key=self.s3_config.credentials.secret_key,
            region_name=self.s3_config.aws_region,  # Used for AWS but not in a DEV env with minio container
            use_ssl=self.s3_config.use_ssl,
        )

        return s3_client

    def bucket_exists(self) -> bool:
        """
        Check if the specified bucket exists.
        """

        try:
            self.s3_client.head_bucket(Bucket=self.s3_config.bucket_name)
            return True
        except self.s3_client.exceptions.ClientError:
            return False

    def create_bucket(self):
        """Create a new bucket.

        Raises:
            Exception: _description_
        """
        if not self.s3_config.create_bucket:
            raise Exception(
                "Could not create bucket since the creation of the bucket is not allowed, check 'create_bucket' flag"
            )

        try:
            self.s3_client.create_bucket(Bucket=self.s3_config.bucket_name)
            print(f"Bucket '{self.s3_config.bucket_name}' created successfully.")
        except Exception as e:
            print(f"Error creating bucket '{self.s3_config.bucket_name}': {e}")

    def get_bucket_files(self):
        """Retrieve all file names in the specified bucket.

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """

        if not self.bucket_exists():
            try:
                self.create_bucket()
            except Exception as e:
                raise Exception(f"An error occured while checking for bucket: {e}")

        file_list = []

        try:
            response = self.s3_client.list_objects_v2(Bucket=self.s3_config.bucket_name)
            if "Contents" in response:
                file_list = [obj["Key"] for obj in response["Contents"]]
        except Exception as e:
            print(f"Error listing files in bucket '{self.s3_config.bucket_name}': {e}")
        return file_list

    def upload_file(self, local_file_path: str, s3_path: str) -> bool:
        """Upload a local file to S3 bucket

        Args:
            local_file_path (str):
            s3_path (str):

        Returns:
            bool: If upload worked
        """

        if not os.path.exists(local_file_path):
            print(f"Error: The file {local_file_path} does not exist.")
            return False

        try:
            # Upload the file
            self.s3_client.upload_file(
                local_file_path, self.s3_config.bucket_name, s3_path
            )
            print(
                f"File '{local_file_path}' uploaded to '{s3_path}' in bucket '{self.s3_config.bucket_name}'."
            )
            return True
        except ClientError as e:
            print(f"Error uploading file '{local_file_path}' to '{s3_path}': {e}")
            return False

    def delete_file(self, s3_file_path: str) -> bool:
        """Delete a file from the S3 bucket.

        Args:
            s3_file_path (str): _description_

        Returns:
            bool: _description_
        """

        try:
            self.s3_client.delete_object(
                Bucket=self.s3_config.bucket_name, Key=s3_file_path
            )
            print(
                f"File '{s3_file_path}' deleted from bucket '{self.s3_config.bucket_name}'."
            )
            return True
        except ClientError as e:
            print(f"Error deleting file '{s3_file_path}': {e}")
            return False

    def get_object_last_modified(self, s3_file_path: str):
        """Retrieve the LastModified time of a file in the S3 bucket."

        Args:
            s3_file_path (str): _description_

        Raises:
            Exception: _description_

        Returns:
            _type_: _description_
        """

        try:
            response = self.s3_client.head_object(
                Bucket=self.s3_config.bucket_name, Key=s3_file_path
            )
            last_modified = response.get("LastModified")
            if last_modified:
                # Ensure the datetime is timezone-aware
                return last_modified.astimezone(timezone.utc)
            else:
                return None
        except ClientError as e:
            raise Exception(f"Error retrieving LastModified for '{s3_file_path}': {e}")
