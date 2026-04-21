"""Logging system for the AI Delivery Platform."""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional

# Default log directory
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "delivery_platform.log"

# Ensure log directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create formatter
formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """Set up logging configuration for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (defaults to logs/delivery_platform.log)
        console_output: Whether to also log to console
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep

    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger("delivery_platform")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # File handler with rotation
    log_file = log_file or str(LOG_FILE)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (optional)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


def get_logger(name: str = "delivery_platform") -> logging.Logger:
    """Get a logger instance for a specific module.

    Args:
        name: Name of the logger (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f"{logging.getLogger('delivery_platform').name}.{name}")


# Global logger instance
logger = setup_logging()


def log_ai_call(func_name: str, prompt_length: int, success: bool, error: Optional[str] = None) -> None:
    """Log AI engine calls."""
    if success:
        logger.info(f"AI call to {func_name} succeeded (prompt length: {prompt_length})")
    else:
        logger.error(f"AI call to {func_name} failed (prompt length: {prompt_length}): {error}")


def log_validation(func_name: str, data_type: str, success: bool, issues: Optional[list] = None) -> None:
    """Log validation operations."""
    if success:
        logger.info(f"Validation passed for {func_name} ({data_type})")
    else:
        issues_str = "; ".join(issues) if issues else "unknown issues"
        logger.warning(f"Validation failed for {func_name} ({data_type}): {issues_str}")


def log_generation(func_name: str, input_count: int, output_count: int, success: bool) -> None:
    """Log generation operations."""
    if success:
        logger.info(f"Generation completed in {func_name}: {input_count} inputs -> {output_count} outputs")
    else:
        logger.error(f"Generation failed in {func_name}: {input_count} inputs")


def log_file_operation(operation: str, file_path: str, success: bool, error: Optional[str] = None) -> None:
    """Log file operations."""
    if success:
        logger.info(f"File {operation} successful: {file_path}")
    else:
        logger.error(f"File {operation} failed: {file_path} - {error}")


def log_pipeline_step(step_name: str, success: bool, duration: Optional[float] = None, error: Optional[str] = None) -> None:
    """Log major pipeline steps."""
    duration_str = f" in {duration:.2f}s" if duration else ""
    if success:
        logger.info(f"Pipeline step '{step_name}' completed successfully{duration_str}")
    else:
        logger.error(f"Pipeline step '{step_name}' failed{duration_str}: {error}")


class LoggedOperation:
    """Context manager for logging operations with timing."""

    def __init__(self, operation_name: str, logger_instance: Optional[logging.Logger] = None):
        self.operation_name = operation_name
        self.logger = logger_instance or logger
        self.start_time = None

    def __enter__(self):
        self.start_time = logging.time.time()
        self.logger.info(f"Starting operation: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = logging.time.time() - self.start_time
        if exc_type is None:
            self.logger.info(f"Operation '{self.operation_name}' completed successfully in {duration:.2f}s")
        else:
            self.logger.error(f"Operation '{self.operation_name}' failed after {duration:.2f}s: {exc_val}")


def handle_exceptions(logger_instance: Optional[logging.Logger] = None):
    """Decorator to handle exceptions gracefully with logging."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            log = logger_instance or logger
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.error(f"Exception in {func.__name__}: {type(e).__name__}: {e}", exc_info=True)
                # Re-raise the exception after logging
                raise
        return wrapper
    return decorator


def log_function_call(logger_instance: Optional[logging.Logger] = None):
    """Decorator to log function calls."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            log = logger_instance or logger
            log.debug(f"Calling {func.__name__} with args: {len(args)} positional, {len(kwargs)} keyword")
            try:
                result = func(*args, **kwargs)
                log.debug(f"Function {func.__name__} completed successfully")
                return result
            except Exception as e:
                log.error(f"Function {func.__name__} failed: {e}")
                raise
        return wrapper
    return decorator