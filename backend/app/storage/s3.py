class S3ObjectStorage:
    name = "s3"

    def __init__(
        self,
        *,
        bucket: str,
        region: str,
        endpoint_url: str | None = None,
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
    ) -> None:
        if not bucket:
            raise ValueError("OBJECT_STORAGE_BUCKET is required for S3 storage")
        import boto3

        self.bucket = bucket
        self._client = boto3.client(
            "s3",
            region_name=region,
            endpoint_url=endpoint_url or None,
            aws_access_key_id=access_key_id or None,
            aws_secret_access_key=secret_access_key or None,
        )

    def put(self, key: str, content: bytes, *, content_type: str) -> str:
        self._client.put_object(Bucket=self.bucket, Key=key, Body=content, ContentType=content_type)
        return key

    def get(self, key: str) -> bytes:
        return self._client.get_object(Bucket=self.bucket, Key=key)["Body"].read()

    def delete(self, key: str) -> None:
        self._client.delete_object(Bucket=self.bucket, Key=key)
