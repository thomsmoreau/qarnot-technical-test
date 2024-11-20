# Requirements

- poetry (for local testing only)
- docker

# Usage with poetry

- **Install poetry**: https://python-poetry.org/docs/
- Run a local Minio container if you need to, the command is given below
- **Example command**: `$ poetry run python s3_synchroniser/main.py --endpoint_url http://S3_HOST:9000 --bucket_name NAME_OF_YOUR_BUCKET --local_path ./data_to_sync --create_bucket True`

# Usage with docker

- Run a minio instance locally:

```
docker run \
               -p 9000:9000 \
               -p 9001:9001 \
               --user $(id -u):$(id -g) \
               --name minio1 \
               -e "MINIO_ROOT_USER=ROOTUSER" \
               -e "MINIO_ROOT_PASSWORD=CHANGEME123" \
               -v /tmp:/data \
               quay.io/minio/minio server /data --console-address ":9001"
```

- Build the image

```
docker build -t s3_synchroniser_image .
```

- Run the sync script (docker inspect to get Minio container IP)

```
docker run --rm \
  -e S3_ACCESS_KEY=your_access_key \
  -e S3_SECRET_KEY=your_secret_key \
  -v PATH_TO_SYNC:/app/data_to_sync \
  s3_synchroniser_image \
  --endpoint_url http://S3_INSTANCE_IP:9000 \
  --bucket_name test \
  --local_path /app/data_to_sync \
  --create_bucket True\
  --aws-region us-east-1
```

# Usage with docker compose

- Check the volume mounted in the docker-compose since this data will be sync
- Check the content of credentials in the .env file
- Check the command arguments passed to the pyth-sync service
- Run: `docker compose up --build`
- Access GUI of minio at localhost:9001 and use credentials from the .env
- ROOT CREDENTIALS IN MINIO SVC from docker-compose.yaml

```
environment:
      MINIO_ROOT_USER: ROOTUSER
      MINIO_ROOT_PASSWORD: CHANGEME123
```

# Notes

- .env not in the .gitignore for dev purpose only
- Add checksum on files in order to compare their content for a better instead of LastModified date ?
- Unit tests to add obviously

# Some links

https://stackoverflow.com/questions/72302266/is-it-possible-to-run-aws-s3-sync-with-boto3
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/boto3.html
https://boto3.amazonaws.com/v1/documentation/api/latest/_modules/boto3.html#client
