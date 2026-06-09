import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "itsstoryday") -> logging.Logger:
    """
    Sets up a logger that outputs to console and a rotating file inside the logs/ directory.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if setup_logger is called multiple times
    if logger.handlers:
        return logger

    # Ensure logs directory exists
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
    os.makedirs(logs_dir, exist_ok=True)
    
    log_file = os.path.join(logs_dir, "app.log")
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler (rotating at 5MB, keeping 3 backups)
    try:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not initialize log file handler: {e}. Logging to console only.")

    return logger
