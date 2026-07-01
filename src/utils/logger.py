import sys
from loguru import logger

def setup_logger(config_slice: dict):
    """
    Configures the loguru logger based on the provided configuration slice.
    
    This follows the Dependency Injection pattern, where the logger setup 
    is decoupled from the global config and only receives what it needs.
    """
    # Remove the default loguru handler to prevent duplicate logs
    logger.remove()

    # Extract variables with defaults from the config slice
    # This ensures the system remains functional even if keys are missing in YAML
    log_level = config_slice.get("level", "INFO").upper()
    file_path = config_slice.get("file_path", "logs/pipeline.log")
    rotation = config_slice.get("rotation", "10 MB")
    retention = config_slice.get("retention", "10 days")

    # Add a standard output handler (Stream)
    # Format provides timestamps, log levels, and the message for console visibility
    logger.add(
        sys.stdout, 
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )

    # Add a file handler (Sink)
    try:
        # Attempt to attach the file sink for persistent observability
        logger.add(
            file_path, 
            rotation=rotation,
            retention=retention,
            level=log_level,
            serialize=False
        )
        logger.debug("File sink successfully attached.")
    except Exception as e:
        # Fallback to standard library if loguru fails to initialize file sink
        # This prevents the application from crashing due to logging infrastructure issues
        import logging
        logging.error(f"Failed to initialize loguru file sink: {e}")
        raise e
