"""Logging utility for the CWAF Sites MCP application."""

import logging
import os

from cwaf_external_mcp.context.context_manager import context_manager


def get_logger(name: str, level: str | None = None) -> logging.Logger:
    """Get a logger with the specified name and level."""
    configure_logging(level=level)
    return logging.getLogger(name)


def configure_logging(level: str | None = None) -> None:
    """Configure the logging settings."""
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(trace_id)s %(message)s - [%(lineno)s]"

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(log_format))
    handler.addFilter(ContextFilter())  # <
    handlers: list[logging.Handler] = [handler]

    logging.basicConfig(
        level=(level if level else os.getenv("LOG_LEVEL", "INFO")).upper(),
        format=log_format,
        handlers=handlers,
    )


class ContextFilter(logging.Filter):
    """A logging filter to add context information to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = context_manager.get_current_trace_id()
        return True
