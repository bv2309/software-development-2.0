from __future__ import annotations

import structlog
from fastapi import FastAPI

logger = structlog.get_logger(__name__)


def setup_tracing(app: FastAPI) -> None:
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    except ImportError:
        logger.info("tracing_disabled", reason="opentelemetry_not_installed")
        return

    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
    logger.info("tracing_enabled")
