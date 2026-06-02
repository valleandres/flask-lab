import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from flask import url_for
from werkzeug.utils import secure_filename

STORAGE_KEY_PATTERN = re.compile(r"^[0-9a-f]{32}_[A-Za-z0-9_.-]+$")


class InvalidStorageKey(ValueError):
    pass


class StorageOperationError(RuntimeError):
    pass


def raise_storage_error(error) -> NoReturn:
    error_code = getattr(error, "response", {}).get("Error", {}).get("Code")
    if error_code in {"404", "NoSuchKey", "NotFound"}:
        raise FileNotFoundError from error
    raise StorageOperationError("Storage service unavailable") from error


def generate_storage_key(filename):
    sanitized_filename = secure_filename(filename or "")
    if not sanitized_filename:
        raise ValueError("Invalid filename")
    return f"{uuid4().hex}_{sanitized_filename}"


def validate_storage_key(key, prefix=""):
    expected_prefix = f"{prefix}/" if prefix else ""
    if not isinstance(key, str) or not key.startswith(expected_prefix):
        raise InvalidStorageKey("Invalid storage key")

    filename = key[len(expected_prefix) :]
    if not STORAGE_KEY_PATTERN.fullmatch(filename):
        raise InvalidStorageKey("Invalid storage key")
    return key


def normalize_prefix(prefix):
    normalized_prefix = (prefix or "").strip("/")
    if not normalized_prefix:
        return ""

    parts = normalized_prefix.split("/")
    if "\\" in normalized_prefix or any(part in {"", ".", ".."} for part in parts):
        raise ValueError("Invalid S3 upload prefix")
    return normalized_prefix


class Storage(ABC):
    @abstractmethod
    def save(self, uploaded_file):
        """Store an uploaded file and return its generated key."""

    @abstractmethod
    def get_url(self, key):
        """Return an access URL for a stored file."""

    @abstractmethod
    def delete(self, key):
        """Delete a stored file."""


class LocalStorage(Storage):
    def __init__(self, upload_folder):
        self.upload_folder = Path(upload_folder).resolve()
        self.upload_folder.mkdir(parents=True, exist_ok=True)

    def save(self, uploaded_file):
        key = generate_storage_key(uploaded_file.filename)
        uploaded_file.save(self._path_for(key))
        return key

    def get_url(self, key):
        self.get_path(key)
        return url_for("files.download_file", key=key, _external=True)

    def delete(self, key):
        self.get_path(key).unlink()

    def get_path(self, key):
        path = self._path_for(key)
        if not path.is_file():
            raise FileNotFoundError(key)
        return path

    def _path_for(self, key):
        return self.upload_folder / validate_storage_key(key)


@dataclass(frozen=True)
class S3StorageConfig:
    bucket_name: str
    upload_prefix: str = ""
    presigned_url_expiration: int = 3600
    aws_profile: str | None = None
    aws_region: str | None = None


class S3Storage(Storage):
    def __init__(self, config, client=None):
        if not config.bucket_name:
            raise ValueError("S3_BUCKET_NAME is required for the s3 storage backend")

        self.bucket_name = config.bucket_name
        self.upload_prefix = normalize_prefix(config.upload_prefix)
        self.presigned_url_expiration = int(config.presigned_url_expiration)
        if self.presigned_url_expiration <= 0:
            raise ValueError("S3_PRESIGNED_URL_EXPIRATION must be positive")
        self.aws_profile = config.aws_profile or None
        self.aws_region = config.aws_region or None
        self._client = client

    @property
    def client(self):
        if self._client is None:
            session = boto3.Session(
                profile_name=self.aws_profile,
                region_name=self.aws_region,
            )
            self._client = session.client("s3")
        return self._client

    def save(self, uploaded_file):
        key = self._key_for_filename(uploaded_file.filename)
        try:
            self.client.upload_fileobj(
                uploaded_file.stream,
                self.bucket_name,
                key,
                ExtraArgs={"ContentType": uploaded_file.mimetype},
            )
        except (BotoCoreError, ClientError) as error:
            raise_storage_error(error)
        return key

    def get_url(self, key):
        validate_storage_key(key, self.upload_prefix)
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=self.presigned_url_expiration,
            )
        except (BotoCoreError, ClientError) as error:
            raise_storage_error(error)

    def delete(self, key):
        validate_storage_key(key, self.upload_prefix)
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
        except (BotoCoreError, ClientError) as error:
            raise_storage_error(error)

    def _key_for_filename(self, filename):
        filename_key = generate_storage_key(filename)
        if not self.upload_prefix:
            return filename_key
        return f"{self.upload_prefix}/{filename_key}"


def create_storage(config):
    backend = str(config.get("STORAGE_BACKEND", "local")).strip().lower()
    if backend == "local":
        return LocalStorage(config.get("LOCAL_UPLOAD_FOLDER", "uploads"))
    if backend == "s3":
        return S3Storage(
            S3StorageConfig(
                bucket_name=config.get("S3_BUCKET_NAME"),
                upload_prefix=config.get("S3_UPLOAD_PREFIX", ""),
                presigned_url_expiration=config.get(
                    "S3_PRESIGNED_URL_EXPIRATION", 3600
                ),
                aws_profile=config.get("AWS_PROFILE"),
                aws_region=config.get("AWS_REGION"),
            )
        )
    raise ValueError(f"Unsupported storage backend: {backend}")
