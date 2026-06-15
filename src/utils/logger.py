import os
from loguru import logger
from src.config.config_loader import cfg

def setup_logging():
    """Configures the loguru logger to write to the path specified in settings.yaml"""
    # Get the logs path from config
    log_path = cfg.get('logs_path')
    
    # Ensure the folder exists
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # Configure loguru to write to a file and print to the console
    # The file name will include the date/time automatically
    logger.add(f"{log_path}/project.log", rotation="10 MB", retention="10 days", level="INFO")
    
    # Also print to the console in a nice format
    logger.add(os.sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: </level>}</level> | {message}")

# Initialize the logger
setup_logging()
