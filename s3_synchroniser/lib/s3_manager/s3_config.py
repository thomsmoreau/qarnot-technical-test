import argparse
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class S3Credentials:
    access_key: str
    secret_key: str

    def __init__(self):
        # Load credentials from environment variables
        self.access_key = os.getenv("S3_ACCESS_KEY")
        self.secret_key = os.getenv("S3_SECRET_KEY")

    # Add post_init for custom value assertions if needed
    def __post_init__(self):
        if not self.access_key or not self.secret_key:
            raise ValueError(
                "S3 credentials are missing from the .env export them as S3_ACCESS_KEY and S3_SECRET_KEY"
            )


@dataclass
class S3Configuration:
    credentials: S3Credentials
    endpoint_url: str
    bucket_name: str
    create_bucket: bool
    local_path: str
    aws_region: Optional[str]


def parse_command_line_args() -> argparse.Namespace:
    """
    Parse command-line arguments for S3 configuration.
    """

    parser = argparse.ArgumentParser(description="S3 configuration flags.")
    parser.add_argument(
        "--endpoint_url",
        required=True,
        dest="endpoint_url",
        help="The S3 endpoint URL.",
    )
    parser.add_argument(
        "--bucket_name",
        dest="bucket_name",
        required=True,
        help="The name of the S3 bucket.",
    )
    parser.add_argument(
        "--local_path",
        dest="local_path",
        required=True,
        help="Local path to synchronize with S3 storage",
    )
    parser.add_argument(
        "--create_bucket",
        dest="create_bucket",
        action="store_true",
        help="Allow creation of the bucket if not present in S3 instance",
    )

    parser.add_argument(
        "--aws-region",
        dest="aws_region",
        default="us-east-1",
        help="The AWS region.",
    )

    parser.set_defaults(
        create_bucket=False,
    )

    return parser.parse_args()


def get_s3_config() -> S3Configuration:
    """
    Function to get S3 configuration.
    Credentials are loaded from the .env file, and other configurations are passed through flags.
    """

    credentials = S3Credentials()

    args = parse_command_line_args()

    # Create the S3Configuration object
    s3_config = S3Configuration(
        credentials=credentials,
        endpoint_url=args.endpoint_url,
        bucket_name=args.bucket_name,
        aws_region=args.aws_region,
        create_bucket=args.create_bucket,
        local_path=args.local_path,
    )

    return s3_config
