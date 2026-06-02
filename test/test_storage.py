from io import BytesIO
from unittest.mock import Mock

import pytest
from werkzeug.datastructures import FileStorage

from app import storage as storage_module
from app.storage import (
    InvalidStorageKey,
    LocalStorage,
    S3Storage,
    S3StorageConfig,
    create_storage,
    generate_storage_key,
    normalize_prefix,
    validate_storage_key,
)


def make_uploaded_file(filename="report.txt", content=b"content"):
    return FileStorage(
        stream=BytesIO(content),
        filename=filename,
        content_type="text/plain",
    )


def test_local_storage_saves_sanitized_file_and_deletes_it(tmp_path):
    storage = LocalStorage(tmp_path / "nested" / "uploads")

    key = storage.save(make_uploaded_file("../../report.txt"))

    assert key.endswith("_report.txt")
    assert storage.get_path(key).read_bytes() == b"content"

    storage.delete(key)

    with pytest.raises(FileNotFoundError):
        storage.get_path(key)


@pytest.mark.parametrize("key", ["../report.txt", "report.txt", 123])
def test_local_storage_rejects_invalid_keys(tmp_path, key):
    storage = LocalStorage(tmp_path)

    with pytest.raises(InvalidStorageKey):
        storage.get_path(key)


def test_generate_storage_key_requires_valid_filename():
    with pytest.raises(ValueError, match="Invalid filename"):
        generate_storage_key("../../")


def test_validate_storage_key_requires_configured_prefix():
    key = f"{'a' * 32}_report.txt"

    assert validate_storage_key(f"uploads/{key}", "uploads") == f"uploads/{key}"

    with pytest.raises(InvalidStorageKey):
        validate_storage_key(key, "uploads")


def test_normalize_prefix():
    assert normalize_prefix("/uploads/nested/") == "uploads/nested"
    assert normalize_prefix("") == ""


@pytest.mark.parametrize(
    "prefix", ["uploads//nested", "uploads/../nested", r"uploads\nested"]
)
def test_normalize_prefix_rejects_unsafe_values(prefix):
    with pytest.raises(ValueError, match="Invalid S3 upload prefix"):
        normalize_prefix(prefix)


def test_s3_storage_uses_private_object_operations():
    client = Mock()
    client.generate_presigned_url.return_value = "https://example.test/presigned"
    storage = S3Storage(
        S3StorageConfig(
            bucket_name="private-bucket",
            upload_prefix="uploads",
            presigned_url_expiration="120",
        ),
        client=client,
    )
    uploaded_file = make_uploaded_file()

    key = storage.save(uploaded_file)
    url = storage.get_url(key)
    storage.delete(key)

    assert key.startswith("uploads/")
    assert key.endswith("_report.txt")
    assert url == "https://example.test/presigned"
    client.upload_fileobj.assert_called_once_with(
        uploaded_file.stream,
        "private-bucket",
        key,
        ExtraArgs={"ContentType": "text/plain"},
    )
    client.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={"Bucket": "private-bucket", "Key": key},
        ExpiresIn=120,
    )
    client.delete_object.assert_called_once_with(Bucket="private-bucket", Key=key)


def test_s3_storage_supports_empty_prefix():
    storage = S3Storage(S3StorageConfig(bucket_name="private-bucket"), client=Mock())

    assert "/" not in storage.save(make_uploaded_file())


def test_s3_storage_requires_bucket_name():
    with pytest.raises(ValueError, match="S3_BUCKET_NAME"):
        S3Storage(S3StorageConfig(bucket_name=""))


def test_s3_storage_requires_positive_presigned_url_expiration():
    with pytest.raises(ValueError, match="must be positive"):
        S3Storage(
            S3StorageConfig(
                bucket_name="private-bucket",
                presigned_url_expiration=0,
            )
        )


def test_s3_storage_rejects_invalid_keys():
    storage = S3Storage(
        S3StorageConfig(bucket_name="private-bucket", upload_prefix="uploads"),
        client=Mock(),
    )

    with pytest.raises(InvalidStorageKey):
        storage.delete("other/report.txt")


def test_s3_storage_creates_boto_client_lazily(monkeypatch):
    client = Mock()
    session = Mock()
    session.client.return_value = client
    boto_session = Mock(return_value=session)
    monkeypatch.setattr(storage_module.boto3, "Session", boto_session)
    storage = S3Storage(
        S3StorageConfig(
            bucket_name="private-bucket",
            aws_profile="",
            aws_region="",
        )
    )

    assert storage.client is client
    assert storage.client is client
    boto_session.assert_called_once_with(profile_name=None, region_name=None)
    session.client.assert_called_once_with("s3")


def test_create_storage_selects_local_backend(tmp_path):
    storage = create_storage(
        {
            "STORAGE_BACKEND": " LOCAL ",
            "LOCAL_UPLOAD_FOLDER": str(tmp_path),
        }
    )

    assert isinstance(storage, LocalStorage)


def test_create_storage_selects_s3_backend():
    storage = create_storage(
        {
            "STORAGE_BACKEND": "s3",
            "S3_BUCKET_NAME": "private-bucket",
            "S3_UPLOAD_PREFIX": "nested/uploads",
            "S3_PRESIGNED_URL_EXPIRATION": 60,
            "AWS_PROFILE": "flask-lab",
            "AWS_REGION": "us-east-1",
        }
    )

    assert isinstance(storage, S3Storage)
    assert storage.bucket_name == "private-bucket"
    assert storage.upload_prefix == "nested/uploads"
    assert storage.presigned_url_expiration == 60
    assert storage.aws_profile == "flask-lab"
    assert storage.aws_region == "us-east-1"


def test_create_storage_rejects_unknown_backend():
    with pytest.raises(ValueError, match="Unsupported storage backend"):
        create_storage({"STORAGE_BACKEND": "missing"})
