"""
Centralized logging configuration for AIUC evaluations.

Provides colored console output and file logging with comprehensive formatting.
"""

import contextvars
import logging
import sys
import colorlog
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional


# Context variable to track current evaluation ID
current_eval_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_eval_id", default=None
)


class EvalContextFilter(logging.Filter):
    """
    Filter that only allows log records from a specific evaluation context.

    When multiple evaluations run concurrently, this filter ensures that
    only logs from the matching eval_id context are written to each file.
    """

    def __init__(self, eval_id: str):
        super().__init__()
        self.eval_id = eval_id

    def filter(self, record: logging.LogRecord) -> bool:
        """Only allow logs where context eval_id matches this filter's eval_id."""
        context_id = current_eval_id.get()
        return context_id == self.eval_id


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = "logs/app.log",
) -> None:
    """Configure logging with colored console output and file logging."""
    # Create logs directory if needed
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()

    # Set to DEBUG to allow all logs to reach handlers
    # Individual handlers will filter based on their own levels
    root_logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s%(reset)s | "
        "%(log_color)s%(levelname)-8s%(reset)s | "
        "%(cyan)s%(name)s:%(funcName)s:%(lineno)d%(reset)s | "
        "%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "white",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        secondary_log_colors={},
        style="%",
    )

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (plain text, no colors)
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel("DEBUG")

        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Log initial setup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized: level={log_level}, file={log_file}")


def get_file_handler(log_file: Path) -> logging.FileHandler:
    """Create and return a file handler for per-evaluation logging."""
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    return file_handler


def log_section(
    logger: logging.Logger,
    level: str,
    title: str,
    content: str | None,
    separator_width: int = 60,
) -> None:
    """Log content with visual separators for readability."""
    if not content:
        return

    separator = "=" * separator_width
    log_method = getattr(logger, level.lower())

    log_method(separator)
    log_method(title)
    log_method(separator)
    log_method(content)
    log_method(separator)


def setup_eval_logger(
    eval_id: str, log_file: Path, log_level: str = "DEBUG"
) -> logging.FileHandler:
    """
    Create a context-filtered file handler for a single evaluation.
    """
    # Create file handler
    file_handler = get_file_handler(log_file)

    # Add context filter to ensure isolation
    context_filter = EvalContextFilter(eval_id)
    file_handler.addFilter(context_filter)

    # Add handler to root logger to capture all logs
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    return file_handler


def cleanup_eval_logger(handler: logging.FileHandler) -> None:
    """
    Clean up an evaluation file handler.
    """
    root_logger = logging.getLogger()

    # Remove handler from root logger
    if handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    # Close the handler
    handler.close()


@contextmanager
def set_eval_context(eval_id: str) -> Generator[None, None, None]:
    """
    Set the current evaluation context for logging.
    """
    token = current_eval_id.set(eval_id)
    try:
        yield
    finally:
        current_eval_id.reset(token)
