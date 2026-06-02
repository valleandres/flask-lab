from flask import Blueprint, current_app, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .extensions import db

health = Blueprint("health", __name__)


@health.get("/health")
def health_check():
    return jsonify({"status": "ok"})


@health.get("/ready")
def readiness_check():
    try:
        db.session.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        db.session.rollback()
        current_app.logger.warning("Readiness database check failed: %s", error)
        return jsonify({"status": "unavailable", "checks": {"database": "error"}}), 503
    return jsonify({"status": "ok", "checks": {"database": "ok"}})
