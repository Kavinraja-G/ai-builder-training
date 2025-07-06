"""
Logging configuration for the Internal Research Agent.
"""
import logging
import sys
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console


def setup_logger(
    name: str = "internal_research_agent",
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with rich formatting and optional file output.

    Args:
        name: Logger name
        level: Logging level
        log_file: Optional file path for logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler with rich formatting
    console_handler = RichHandler(
        console=Console(),
        show_time=True,
        show_path=False,
        markup=True
    )
    console_handler.setLevel(getattr(logging, level.upper()))

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Default logger instance - quiet by default
logger = setup_logger(level="WARNING")