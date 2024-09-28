import json
import logging
import os
import sys
import uuid
from collections.abc import Callable
from enum import Enum
from typing import TYPE_CHECKING

from loguru import logger
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    SimpleLogRecordProcessor,
)
from opentelemetry.sdk.resources import Resource

from informed.config import Config
from informed.logger.log_types import LogLevels

if TYPE_CHECKING:
    from loguru import Record


def _filter_uvicorn_health_access_logs() -> None:
    def filter_health(log_record: logging.LogRecord) -> bool:
        return "GET /api/v1/health" not in log_record.getMessage()

    def filter_metrics(log_record: logging.LogRecord) -> bool:
        return "GET /metrics" not in log_record.getMessage()

    logging.getLogger("uvicorn.access").addFilter(filter_health)
    logging.getLogger("uvicorn.access").addFilter(filter_metrics)


def setup_logger(config: Config, override_level: str | None = None) -> None:
    logger.remove()

    if (
        config.telemetry_config.enabled
        and config.telemetry_config.opentelemetry_config.enabled
    ):
        _opentelemetry_logging(config)
    else:
        # only forward uvicorn logging if otel is disabled. otherwise two loguru handlers collide
        _uvicorn_loguru_loging()

    _set_levels()
    _filter_uvicorn_health_access_logs()
    if config.logging_config.enable_console:
        _loguru_sink(config, override_level)


def _loguru_sink_filters(level: str) -> Callable:
    def custom_filters(record: str | Callable | dict | None) -> bool:
        if not isinstance(record, dict):
            return True

        # Filter out diagnostic logs from this sink if we're not printing DEBUG logs.
        if level != "DEBUG" and "level" in record:
            record_level = record["level"]
            if (
                hasattr(
                    record_level, "no"
                )  # have to compare using tuple as type loguru.Level is not exposed
                and record_level.no
                == LogLevels.DIAGNOSTIC.value  # pyright: ignore[reportAttributeAccessIssue]
            ):
                return False

        # Convert Enums to human-readable strings (for categories and subcategories)
        if "extra" in record:
            extra = record["extra"]
            if isinstance(extra, dict):
                for key in extra.copy():
                    if isinstance(key, str) and isinstance(extra[key], Enum):
                        extra[key] = extra[key].value
                    if isinstance(key, Enum):
                        extra[key.value] = extra.pop(key)
        return True

    return custom_filters


def _loguru_unwrapping_sink(level: str, is_jsonify: bool) -> Callable:
    def unwrapping_sink(message: str) -> None:
        if is_jsonify:
            message_dict = json.loads(message)
            sys.stdout.write(json.dumps(message_dict["record"]) + "\n")
        else:
            sys.stdout.write(message)

    return unwrapping_sink


def _loguru_sink(config: Config, override_level: str | None = None) -> None:
    level = (
        override_level.upper()
        if override_level
        else config.logging_config.level.upper()
    )

    logger.add(
        _loguru_unwrapping_sink(level, config.logging_config.jsonify),
        serialize=config.logging_config.jsonify,
        colorize=(not config.logging_config.jsonify),
        backtrace=True,
        level=level,
        format=(
            ""
            if config.logging_config.jsonify
            else (
                "<green>{time:YYYY-MM-DD HH:mm:ss!UTC} UTC</green> | "
                "<level>{level: <6}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "{extra} - <level>{message}</level>"
            )
        ),
        filter=_loguru_sink_filters(level),  # type: ignore[arg-type]
    )


def _uvicorn_loguru_loging() -> None:
    loggers = (
        logging.getLogger(name)
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn.")
    )

    for uvicorn_logger in loggers:
        uvicorn_logger.handlers = []

    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            level = logger.level(record.levelname).name

            def patch_function_and_line(loguru_record: "Record") -> None:
                loguru_record["name"] = "uvicorn"
                loguru_record["module"] = record.module
                loguru_record["function"] = record.funcName
                loguru_record["line"] = record.lineno

            logger.patch(patch_function_and_line).opt(exception=record.exc_info).log(
                level, record.getMessage()
            )

        # change handler for default uvicorn logger

    intercept_handler = InterceptHandler()
    logging.getLogger("uvicorn").handlers = [intercept_handler]


def _opentelemetry_logging(config: Config) -> None:
    # Set up root otel logger
    _setup_otel_logger(config)
    logger.info("Instrumented loguru with OpenTelemetry")


def _fix_extras_loguru(record: logging.LogRecord) -> None:
    if hasattr(record, "extra"):
        extra = record.__dict__["extra"]
        for key in extra:
            if isinstance(extra[key], Enum):
                extra[key] = extra[key].value
            record.__dict__[key] = extra[key]


def _setup_otel_logger(config: Config) -> None:
    class FixExtrasAndPropagateToLoggingHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            _fix_extras_loguru(record)
            logging.getLogger(record.name).handle(record)

    class FixExtrasHandler(logging.Handler):
        def __init__(self, base_handler: logging.Handler):
            super().__init__()
            self.base_handler = base_handler

        def emit(self, record: logging.LogRecord) -> None:
            _fix_extras_loguru(record)
            self.base_handler.handle(record)

    # Create logger providers
    default_logger_provider = LoggerProvider(resource=create_otel_resource(config))
    trace_logger_provider = LoggerProvider(resource=create_otel_resource(config))
    set_logger_provider(default_logger_provider)  # Set the global logger provider

    # Create processors.
    # Note: There is no anonymization processors in the trace processor as Langsmith
    # traces will be processed in the instrumentation layer.
    # Batching the logs is also unnecessary as the logs are typically large and infrequent.
    oltp_exporter = OTLPLogExporter(insecure=True)
    batch_log_record_processor = BatchLogRecordProcessor(oltp_exporter)

    default_logger_provider.add_log_record_processor(batch_log_record_processor)
    trace_logger_provider.add_log_record_processor(
        SimpleLogRecordProcessor(oltp_exporter)
    )

    # loguru only supports one logger. So we need to conditionally associate different handlers.
    # Create the default handler
    default_handler: logging.Handler = LoggingHandler(
        logger_provider=default_logger_provider
    )
    LoggingInstrumentor().instrument(set_logging_format=True)
    logger.add(
        FixExtrasAndPropagateToLoggingHandler(),
        format="{message}",
        level=config.logging_config.level,
    )
    root_logger = logging.getLogger()
    root_logger.addHandler(default_handler)
    # remove extra console logger, since we have the loguru logger below
    for log_handler in root_logger.handlers[:]:
        if isinstance(log_handler, logging.StreamHandler):
            root_logger.removeHandler(log_handler)

    # Create handler for Langsmith traces.
    trace_handler: logging.Handler = LoggingHandler(
        logger_provider=trace_logger_provider
    )
    logger.add(
        FixExtrasHandler(trace_handler),
        format="{message}",
        level=config.logging_config.level,
    )


def _set_levels() -> None:
    # Mute false warning from Open Telemetry attributes checker
    logging.getLogger("opentelemetry.attributes").setLevel("ERROR")
    logging.getLogger("httpx").setLevel("WARN")
    # Add custom levels if they don't already exist
    if LogLevels.DIAGNOSTIC.name not in logging.getLevelNamesMapping():
        logging.addLevelName(
            LogLevels.DIAGNOSTIC.value, LogLevels.DIAGNOSTIC.name
        )  # Without this, the OLTP log level name mapping won't work
    try:
        _ = logger.level(LogLevels.DIAGNOSTIC.name)
    except ValueError:
        # Add the level
        logger.level(
            LogLevels.DIAGNOSTIC.name, LogLevels.DIAGNOSTIC.value, color="<yellow><dim>"
        )


instance_id = str(uuid.uuid4())


def create_otel_resource(config: Config) -> Resource:
    return Resource.create(
        attributes={
            "service.name": config.service_name,
            "service.instance.id": instance_id,
            "informed.version": os.getenv("APP_VERSION", ""),
        }
    )
