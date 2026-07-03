import logging
import sys
from app.utils.config import settings

def setup_logging():
    """
    Sets up the centralized logging configuration for the Kavalar backend.
    Logs to stdout with a clean format.
    """
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )
    
    # Optional: Suppress noisy external dependencies
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Run initial setup
setup_logging()

# Expose a default logger for the app module
logger = logging.getLogger("kavalar")
