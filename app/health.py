from flask import Blueprint, current_app, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .cache_utils import cache_readiness_status
from .extensions import db

health = Blueprint("health", __name__)


@health.get("/health")
def health_check():
    return jsonify({"status": "ok"})


@health.get("/ready")
def readiness_check():
    checks = {}

    try:
        db.session.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        db.session.rollback()
        current_app.logger.warning("Readiness database check failed: %s", error)
        checks["database"] = "error"
        return jsonify({"status": "unavailable", "checks": checks}), 503

    checks["database"] = "ok"

    cache_status = cache_readiness_status(current_app.config)
    if cache_status != "skipped":
        checks["cache"] = cache_status
    if cache_status == "error":
        return jsonify({"status": "unavailable", "checks": checks}), 503

    return jsonify({"status": "ok", "checks": checks})
