
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.aiohttp_client import (  # pyright: ignore[reportMissingTypeStubs]
    AioHttpClientInstrumentor,
)
from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor  # pyright: ignore[reportMissingTypeStubs]
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor  # pyright: ignore[reportMissingTypeStubs]
from opentelemetry.instrumentation.logging import LoggingInstrumentor  # pyright: ignore[reportMissingTypeStubs]
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor  # pyright: ignore[reportMissingTypeStubs]
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs import LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from victreebot.utils.EnvVarLoader import EnvVarLoader

if TYPE_CHECKING:
    import aiohttp
    import requests
    from opentelemetry.trace.span import Span

    from victreebot.core.bot import Bot


from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


def setup_opentelemetry(bot: Bot) -> tuple[TracerProvider | None, LoggerProvider | None]:
    SEQ_API_KEY = EnvVarLoader.load_optional_env_variable("SEQ_API_KEY")
    if not SEQ_API_KEY:
        logging.getLogger(__name__).warning(
            "SEQ_API_KEY is not set. OpenTelemetry will not be configured."
        )
        return None, None

    """Configure opentelemetry for distributed tracing."""
    resource = Resource.create({"service.name": bot.vars.SERVICE_NAME})

    # -------- TRACING --------
    tracer_provider = TracerProvider(resource=resource)
    span_exporter = OTLPSpanExporter(
        endpoint=bot.vars.SEQ_ENDPOINT_TRACES,
        headers={"X-Seq-ApiKey": SEQ_API_KEY},
    )
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(tracer_provider)

    set_global_textmap(CompositePropagator([TraceContextTextMapPropagator(), W3CBaggagePropagator()]))

    # -------- LOGGING --------
    logger_provider = LoggerProvider(resource=resource)
    log_exporter = OTLPLogExporter(
        endpoint=bot.vars.SEQ_ENDPOINT_LOGS,
        headers={"X-Seq-ApiKey": SEQ_API_KEY},
    )
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    handler = LoggingHandler(
        level=logging.getLevelNamesMapping()[bot.vars.LOG_LEVEL.upper()],  # type: ignore[attr-defined]
        logger_provider=logger_provider,
    )

    # Attach handler to Python root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(bot.vars.LOG_LEVEL.upper())
    root_logger.addHandler(handler)

    LoggingInstrumentor().instrument()
    RequestsInstrumentor().instrument(response_hook=requests_response_hook)
    AioHttpClientInstrumentor().instrument()
    AsyncioInstrumentor().instrument(response_hook=aiohttp_client_response_hook)
    URLLib3Instrumentor().instrument()
    AsyncPGInstrumentor().instrument()  # type: ignore[no-untyped-call]
    RedisInstrumentor().instrument(tracer_provider=tracer_provider)  # pyright: ignore[reportUnknownMemberType]

    return tracer_provider, logger_provider


# Override hooks
def requests_response_hook(span: Span, request_obj: requests.PreparedRequest, response: requests.Response) -> None:
    """Override the requests response hook."""
    span.update_name(f"{request_obj.method} {request_obj.url}")
    span.set_attribute("http.method", f"{request_obj.method}")
    span.set_attribute("http.url", str(request_obj.url))
    span.set_attribute("http.status_code", str(response.status_code))


def aiohttp_client_response_hook(
    span: Span, params: aiohttp.TraceRequestEndParams | aiohttp.TraceRequestExceptionParams
) -> None:
    """Override the aiohttp client response hook."""
    span.update_name(f"{params.method} {params.url}")