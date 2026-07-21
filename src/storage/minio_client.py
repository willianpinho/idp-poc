import io

from minio import Minio
from minio.error import S3Error

from src.config import settings

_client: Minio | None = None


def get_minio_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_use_ssl,
        )
        # Ensure bucket exists
        if not _client.bucket_exists(settings.minio_bucket):
            _client.make_bucket(settings.minio_bucket)
    return _client


def upload_file(storage_key: str, data: bytes, content_type: str = "application/pdf") -> str:
    client = get_minio_client()
    client.put_object(
        settings.minio_bucket,
        storage_key,
        io.BytesIO(data),
        length=len(data),
        content_type=content_type,
    )
    return storage_key


def download_file(storage_key: str) -> bytes:
    client = get_minio_client()
    response = client.get_object(settings.minio_bucket, storage_key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def get_presigned_url(storage_key: str, expires_hours: int = 1) -> str:
    from datetime import timedelta

    client = get_minio_client()
    return client.presigned_get_object(
        settings.minio_bucket,
        storage_key,
        expires=timedelta(hours=expires_hours),
    )


def delete_file(storage_key: str):
    client = get_minio_client()
    try:
        client.remove_object(settings.minio_bucket, storage_key)
    except S3Error:
        pass
