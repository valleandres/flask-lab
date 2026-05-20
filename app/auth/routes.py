from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash

from app.auth.jwt_utils import generate_token, decode_token
from app.extensions import csrf
from app.models import Admin

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
@csrf.exempt
def login():
    data = request.get_json() or {}
    user = Admin.query.filter_by(username=data.get("username")).first()

    if user and check_password_hash(user.password, data.get("password", "")):
        token = generate_token(user_id=user.id)
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
