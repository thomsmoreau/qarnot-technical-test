import os
from datetime import datetime, timezone

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
            region_name=self.s3_config.aws_region,
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
            raise PermissionError(
                "Could not create bucket since the creation not allowed, check 'create_bucket' flag"
            )

        try:
            self.s3_client.create_bucket(Bucket=self.s3_config.bucket_name)
            print(f"Bucket '{self.s3_config.bucket_name}' created successfully.")
        except Exception as e:
            raise ClientError(
                error_response={
                    "Error": {"Message": f"Failed to create bucket: {str(e)}"}
                },
                operation_name="create_bucket",
            ) from e

    def get_bucket_files(self) -> list[str]:
        """Retrieve all file names in the specified bucket.

        Returns:
            list[str]: List of file paths (keys) in the bucket

        Raises:
            Exception: If bucket creation fails or listing objects fails
        """
        if not self.bucket_exists():
            try:
                self.create_bucket()
            except Exception as e:
                raise ClientError(
                    error_response={
                        "Error": {"Message": f"Failed to create bucket: {str(e)}"}
                    },
                    operation_name="create_bucket",
                ) from e

        file_list = []
        paginator = self.s3_client.get_paginator("list_objects_v2")

        try:
            for page in paginator.paginate(Bucket=self.s3_config.bucket_name):
                if "Contents" in page:
                    file_list.extend(obj["Key"] for obj in page["Contents"])
            return file_list
        except ClientError as e:
            raise e

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

    def get_object_last_modified(self, s3_file_path: str) -> datetime | None:
        """Retrieve the LastModified timestamp of a file in the S3 bucket.

        Args:
            s3_file_path (str): The path (key) of the file in the S3 bucket

        Returns:
            datetime | None: The UTC timestamp when the file was last modified,
                           or None if LastModified information is not available

        Raises:
            ClientError: If there's an error accessing the S3 object or if the file doesn't exist
        """

        try:
            response = self.s3_client.head_object(
                Bucket=self.s3_config.bucket_name, Key=s3_file_path
            )
            last_modified = response.get("LastModified")
            return last_modified.astimezone(timezone.utc) if last_modified else None
        except ClientError as e:
            LOGGER.error("Error retrieving LastModified for '%s': %s", s3_file_path, e)
            raise
