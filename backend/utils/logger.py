"""Logging utility for WireGuard Manager."""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    name: str = 'wireguard-manager',
    level: str = 'INFO',
    method: str = 'console',
    log_dir: Optional[str] = None,
    max_bytes: int = 10485760,
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up and configure logger.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        method: Logging method - 'console' for stdout, 'directory' for file logging
        log_dir: Directory for log files (required if method='directory')
        max_bytes: Maximum size of each log file in bytes
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Set logging level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    if method == 'directory':
        # File-based logging
        if not log_dir:
            raise ValueError("log_dir is required when method='directory'")
        
        # Create log directory if it doesn't exist
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handlers for different log levels
        # Main log file - all messages
        main_handler = RotatingFileHandler(
            f"{log_dir}/wireguard-manager.log",
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        main_handler.setFormatter(formatter)
        main_handler.setLevel(log_level)
        logger.addHandler(main_handler)
        
        # Error log file - errors and above
        error_handler = RotatingFileHandler(
            f"{log_dir}/wireguard-manager-error.log",
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        logger.addHandler(error_handler)
        
        logger.info(f"File logging initialized: {log_dir}")
    else:
        # Console logging (default)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)
        
        logger.info("Console logging initialized")
    
    return logger


def get_logger(name: str = 'wireguard-manager') -> logging.Logger:
    """
    Get existing logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
