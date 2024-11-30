# S3 Synchronizer

A Python utility to synchronize local directories with S3-compatible object storage services, with support for MinIO and AWS S3.

## Features

- 🔄 **Bidirectional Sync**: Synchronize files between local directories and S3 storage
- 🔌 **S3 Compatibility**: Works with any S3-compatible storage (AWS S3, MinIO, etc.)
- 🐳 **Container Ready**: Full Docker and Docker Compose support
- ⚙️ **Flexible Configuration**: Command-line options and environment variables
- 🔐 **Secure**: Support for authentication and SSL/TLS connections

## Prerequisites

- Python 3.7+
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- Docker (optional, for containerized usage)

## Quick Start

1. **Clone and Install**

   ```bash
   git clone https://github.com/yourusername/s3_synchronizer.git
   cd s3_synchronizer
   poetry install
   ```

2. **Basic Usage**
   ```bash
   poetry run python s3_synchronizer/main.py \
     --endpoint_url http://localhost:9000 \
     --bucket_name my-bucket \
     --local_path ./data \
     --create_bucket True
   ```

## Usage Options

### 1. Poetry (Local Development)

Start a local MinIO server (optional):

```bash
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=ROOTUSER" \
  -e "MINIO_ROOT_PASSWORD=CHANGEME123" \
  -v /tmp:/data \
  minio/minio server /data --console-address ":9001"
```

Run the synchronization script:

```bash
poetry run python s3_synchronizer/main.py \
  --endpoint_url http://localhost:9000 \
  --bucket_name my-bucket \
  --local_path ./data \
  --create_bucket True
```

### 2. Docker (Containerized Usage)

Build the Docker image:

```bash
docker build -t s3_synchronizer_image .
```

Run the MinIO container (if not already running):

```bash
docker run \
  -p 9000:9000 \
  -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=ROOTUSER" \
  -e "MINIO_ROOT_PASSWORD=CHANGEME123" \
  -v /tmp:/data \
  minio/minio server /data --console-address ":9001"
```

Run the synchronization script using Docker (Add the `--create_bucket` flag only if you want to create the bucket):

```bash
docker run --rm \
  -e S3_ACCESS_KEY=ROOTUSER \
  -e S3_SECRET_KEY=CHANGEME123 \
  -v PATH_TO_SYNC:/app/data \
  s3_synchronizer_image \
  --endpoint_url http://MINIO_CONTAINER_IP:9000 \
  --bucket_name test \
  --local_path /app/data \
  --create_bucket
```

### 3. Docker Compose (Containerized Usage)

Configure environment variables in `.env` file:

```bash
S3_ACCESS_KEY=ROOTUSER
S3_SECRET_KEY=CHANGEME123
```

Customize the synchronization settings in `docker-compose.yml`:

```yaml
services:
  sync-pyth:
    # ... other settings ...
    command: >
      --endpoint_url http://minio:9000        # URL of your MinIO/S3 service
      --bucket_name test                      # Name of your bucket
      --local_path /app/data_to_sync         # Container path to sync
      --create_bucket                        # Optional: creates bucket if missing
    volumes:
      - ./data_to_sync:/app/data_to_sync # Local path:Container path
```

Run Docker Compose:

```bash
docker-compose up --build
```

Access the MinIO GUI:

```bash
Open your browser and navigate to http://localhost:9001.
Log in using ROOTUSER/CHANGEME123.
```

## Configuration

The synchronization script accepts the following command-line arguments:

- `--endpoint_url`: The URL of the S3-compatible service (required)
- `--bucket_name`: The name of the bucket to sync with (required)
- `--local_path`: The local directory path to synchronize (required)
- `--create_bucket`: Allow creation of the bucket if not present in S3 instance (optional, defaults to False)
- `--use_ssl`: Use SSL to connect to the S3 instance (optional, defaults to False)
- `--aws-region`: The AWS region (optional, defaults to us-east-1)

Environment variables required:

- `S3_ACCESS_KEY`: Your S3 access key
- `S3_SECRET_KEY`: Your S3 secret key

## Deployment Strategy

### Production Deployment

1. **Build and push the Production Image**

   ```bash
   docker build -t s3_synchronizer:prod --target production .
   docker push your-registry/s3_synchronizer:prod
   ```

2. **Environment Configuration**

   - Create a `.env.prod` file:

   ```bash
   S3_ACCESS_KEY=your_access_key
   S3_SECRET_KEY=your_secret_key
   S3_ENDPOINT_URL=https://your-s3-endpoint
   S3_BUCKET_NAME=your-bucket
   AWS_REGION=your-region
   ```

3. **Deployment Options**

   a. **Standalone Docker**

   ```bash
   docker run --rm \
     --env-file .env.prod \
     -v /path/to/data:/app/data \
     s3_synchronizer:prod
   ```

   b. **Docker Compose Production**

   ```yaml
   # docker-compose.prod.yml
   version: "3.8"
   services:
     s3_synchronizer:
       image: s3_synchronizer:prod
       env_file: .env.prod
       volumes:
         - /path/to/data:/app/data
       restart: unless-stopped
   ```

   Deploy with:

   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Security Considerations**
   - Use secrets management for sensitive credentials
   - Use read-only file system where possible

## Notes

- The .env file is not included in .gitignore for development purposes only. Ensure you don't commit sensitive information.
- Consider adding checksums on files to compare their content instead of relying solely on the LastModified date for better synchronization accuracy.
- Unit tests are planned to be added in future updates.
- Additional basic improvements needed:
  - Add basic file validation before transfer to prevent corruption
  - Implement simple retry logic for failed operations
  - Improve error handling and reporting
  - Add basic file exclusion support (e.g., temporary files)
  - Implement proper cleanup on script interruption
