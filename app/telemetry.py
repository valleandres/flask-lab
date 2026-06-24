import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.extensions import db

_TELEMETRY_INITIALIZED = False


def init_telemetry(app):
    global _TELEMETRY_INITIALIZED  # pylint: disable=global-statement

    if not app.config.get("OTEL_ENABLED", True) or _TELEMETRY_INITIALIZED:
        return

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

    resource = Resource.create(
        {
            "service.name": "flask-lab",
            "service.version": os.getenv("OTEL_SERVICE_VERSION", "1"),
            "deployment.environment": app.config["APP_ENV"],
        }
    )

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
    )
    trace.set_tracer_provider(provider)

    FlaskInstrumentor().instrument_app(
        app, excluded_urls=app.config["OTEL_EXCLUDED_URLS"]
    )

    with app.app_context():
        SQLAlchemyInstrumentor().instrument(engine=db.engine)

    RequestsInstrumentor().instrument()

    _TELEMETRY_INITIALIZED = True
