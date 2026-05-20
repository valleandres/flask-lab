import redis
from flask import Blueprint, current_app, jsonify, request

from app.extensions import cache

from . import csrf
from .models import User, db

USER_SORT_COLUMNS = {
    "id": User.id,
    "name": User.name,
}


def invalidate_users_cache():
    if current_app.config.get("CACHE_TYPE") != "RedisCache":
        return

    redis_client = redis.Redis.from_url(current_app.config["CACHE_REDIS_URL"])
    keys = redis_client.keys("*api/users*")
    if keys:
        redis_client.delete(*keys)


api = Blueprint("api", __name__, url_prefix="/api/users")
csrf.exempt(api)


def filter_users_by_name(query, name_filter):
    if not name_filter:
        return query
    return query.filter(User.name.ilike(f"%{name_filter}%"))


def sort_users(query, sort_field, sort_order):
    sort_column = USER_SORT_COLUMNS.get(sort_field, User.id)
    if sort_order == "desc":
        return query.order_by(sort_column.desc())
    return query.order_by(sort_column.asc())


@api.route("", methods=["GET"])
@cache.cached(timeout=60)
def get_users():
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=2, type=int)
    name_filter = request.args.get("name")
    sort_field = request.args.get("sort", default="id")
    sort_order = request.args.get("order", default="asc")

    query = User.query
    query = filter_users_by_name(query, name_filter)
    query = sort_users(query, sort_field, sort_order)

    users_query = query.paginate(page=page, per_page=limit, error_out=False)

    users = users_query.items

    return jsonify(
        {
            "page": page,
            "limit": limit,
            "total": users_query.total,
            "pages": users_query.pages,
            "data": [{"id": u.id, "name": u.name} for u in users],
        }
    )


@api.route("/<int:user_id>", methods=["GET"])
@cache.cached(timeout=60)
def get_user(user_id):
    user = db.get_or_404(User, user_id)
    return jsonify({"id": user.id, "name": user.name})


@api.route("", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Missing name"}), 400
    user = User(name=data["name"])
    db.session.add(user)
    db.session.commit()
    invalidate_users_cache()
    return jsonify({"id": user.id, "name": user.name}), 201


@api.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = db.get_or_404(User, user_id)
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Missing name"}), 400
    user.name = data["name"]
    db.session.commit()
    invalidate_users_cache()
    return jsonify({"id": user.id, "name": user.name})


@api.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    invalidate_users_cache()
    return "", 204
