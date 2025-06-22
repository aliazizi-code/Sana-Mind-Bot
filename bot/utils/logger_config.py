# logger_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    info_handler = RotatingFileHandler(
        os.path.join(log_dir, 'info.log'),
        maxBytes=1_000_000,
        backupCount=3,
        encoding='utf-8'
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'errors.log'),
        maxBytes=1_000_000,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    debug_handler = RotatingFileHandler(
        os.path.join(log_dir, 'debug.log'),
        maxBytes=2_000_000,
        backupCount=7,
        encoding='utf-8'
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[info_handler, error_handler, debug_handler, console_handler]
    )

setup_logging()