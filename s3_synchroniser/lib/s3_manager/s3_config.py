import argparse
import os
from ast import arg
from dataclasses import dataclass
from typing import Optional


@dataclass
class S3Credentials:
    access_key: str
    secret_key: str


@dataclass
class S3Configuration:
    credentials: S3Credentials
    endpoint_url: str
    bucket_name: str
    create_bucket: bool
    local_path: str
    aws_region: Optional[str]


def get_credentials_from_env() -> S3Credentials:
    # Load credentials from environment variables
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")

    if not access_key or not secret_key:
        raise ValueError(
            "S3 credentials are missing from the .env export them as S3_ACCESS_KEY and S3_SECRET_KEY"
        )

    return S3Credentials(access_key=access_key, secret_key=secret_key)


def parse_command_line_args() -> argparse.Namespace:
    """
    Parse command-line arguments for S3 configuration.
    """

    parser = argparse.ArgumentParser(description="S3 configuration flags.")
    parser.add_argument(
        "--endpoint_url",
        required=True,
        help="The S3 endpoint URL.",
    )
    parser.add_argument(
        "--bucket_name",
        required=True,
        help="The name of the S3 bucket.",
    )
    parser.add_argument(
        "--local_path",
        required=True,
        help="Local path to synchronize with S3 storage",
    )
    parser.add_argument(
        "--create_bucket",
        type=bool,
        default=False,
        help="Allow creation of the bucket if not present",
    )
    parser.add_argument(
        "--aws-region",
        default="us-east-1",
        help="The AWS region.",
    )

    return parser.parse_args()


def get_s3_config() -> S3Configuration:
    """
    Function to get S3 configuration.
    Credentials are loaded from the .env file, and other configurations are passed through flags.
    """

    credentials = get_credentials_from_env()

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
