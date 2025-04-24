from flask import Blueprint, request, jsonify
from app.auth.jwt_utils import generate_token, decode_token
from app.extensions import csrf

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
@csrf.exempt
def login():
    data = request.json
    if data["username"] == "admin" and data["password"] == "123": # FIXME
        token = generate_token(user_id=1)
        return jsonify(token=token)
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route("/protected", methods=["GET"])
def protected():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Missing token"}), 401

    token = auth_header.replace("Bearer ", "")
    user_id = decode_token(token)
    if not user_id:
        return jsonify({"error": "Invalid or expired token"}), 401

    return jsonify({"message": f"Access granted for user {user_id}."})