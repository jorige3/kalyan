import logging
import sys
from pathlib import Path

def setup_logger(name: str, log_file: str = "logs/project.log", level=logging.INFO):
    """Sets up a logger with console and file handlers."""
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create handlers
    c_handler = logging.StreamHandler(sys.stdout)
    f_handler = logging.FileHandler(log_file)
    c_handler.setLevel(level)
    f_handler.setLevel(level)
    
    # Create formatters and add it to handlers
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    c_format = logging.Formatter(format_str)
    f_format = logging.Formatter(format_str)
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    
    # Add handlers to the logger
    if not logger.handlers:
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
        
    return logger
