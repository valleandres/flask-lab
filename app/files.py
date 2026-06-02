from flask import Blueprint, abort, current_app, jsonify, request, send_file

from .extensions import csrf
from .storage import InvalidStorageKey, LocalStorage

files = Blueprint("files", __name__)
csrf.exempt(files)


def get_storage():
    return current_app.extensions["storage"]


def get_requested_key():
    return request.args.get("key")


@files.post("/files")
def upload_file():
    uploaded_file = request.files.get("file")
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"error": "Missing file"}), 400

    try:
        key = get_storage().save(uploaded_file)
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    return jsonify({"key": key}), 201


@files.get("/files/url")
def get_file_url():
    key = get_requested_key()
    if not key:
        return jsonify({"error": "Missing key"}), 400

    try:
        url = get_storage().get_url(key)
    except InvalidStorageKey as error:
        return jsonify({"error": str(error)}), 400
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    return jsonify({"key": key, "url": url})


@files.delete("/files")
def delete_file():
    key = get_requested_key()
    if not key:
        return jsonify({"error": "Missing key"}), 400

    try:
        get_storage().delete(key)
    except InvalidStorageKey as error:
        return jsonify({"error": str(error)}), 400
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    return "", 204


@files.get("/files/content")
def download_file():
    key = get_requested_key()
    if not key:
        return jsonify({"error": "Missing key"}), 400

    storage = get_storage()
    if not isinstance(storage, LocalStorage):
        abort(404)

    try:
        path = storage.get_path(key)
    except InvalidStorageKey as error:
        return jsonify({"error": str(error)}), 400
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    return send_file(path)
