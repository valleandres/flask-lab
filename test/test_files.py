from io import BytesIO
from unittest.mock import Mock
from urllib.parse import urlsplit

from app.storage import S3Storage, S3StorageConfig


def test_local_file_lifecycle(client, app):
    upload_response = client.post(
        "/files",
        data={"file": (BytesIO(b"hello"), "../../hello.txt")},
    )

    assert upload_response.status_code == 201
    key = upload_response.get_json()["key"]
    assert key.endswith("_hello.txt")
    assert app.extensions["storage"].get_path(key).read_bytes() == b"hello"

    url_response = client.get("/files/url", query_string={"key": key})

    assert url_response.status_code == 200
    url = url_response.get_json()["url"]
    split_url = urlsplit(url)
    content_response = client.get(f"{split_url.path}?{split_url.query}")
    assert content_response.status_code == 200
    assert content_response.data == b"hello"

    delete_response = client.delete("/files", query_string={"key": key})

    assert delete_response.status_code == 204
    assert not app.extensions["storage"].upload_folder.joinpath(key).exists()


def test_upload_requires_file(client):
    response = client.post("/files")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing file"}


def test_upload_rejects_invalid_filename(client):
    response = client.post("/files", data={"file": (BytesIO(b"hello"), "../../")})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid filename"}


def test_file_url_requires_key(client):
    response = client.get("/files/url")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing key"}


def test_file_url_rejects_invalid_key(client):
    response = client.get("/files/url", query_string={"key": "../secret.txt"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid storage key"}


def test_file_url_returns_not_found(client):
    response = client.get("/files/url", query_string={"key": f"{'a' * 32}_missing.txt"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "File not found"}


def test_delete_requires_key(client):
    response = client.delete("/files")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing key"}


def test_delete_rejects_invalid_key(client):
    response = client.delete("/files", query_string={"key": "../secret.txt"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid storage key"}


def test_delete_returns_not_found(client):
    response = client.delete("/files", query_string={"key": f"{'a' * 32}_missing.txt"})

    assert response.status_code == 404
    assert response.get_json() == {"error": "File not found"}


def test_download_requires_key(client):
    response = client.get("/files/content")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing key"}


def test_download_rejects_invalid_key(client):
    response = client.get("/files/content", query_string={"key": "../secret.txt"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid storage key"}


def test_download_returns_not_found(client):
    response = client.get(
        "/files/content",
        query_string={"key": f"{'a' * 32}_missing.txt"},
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "File not found"}


def test_download_is_not_available_for_s3_backend(client, app):
    app.extensions["storage"] = S3Storage(
        S3StorageConfig(bucket_name="private-bucket"),
        client=Mock(),
    )

    response = client.get("/files/content", query_string={"key": "unused"})

    assert response.status_code == 404
