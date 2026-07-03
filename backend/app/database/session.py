from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.utils.config import settings
from app.utils.logger import logger

# Create the SQLAlchemy engine and configure fallback options
logger.info("Initializing database connection engine.")

db_url = settings.database_url_sqlalchemy
engine_args = {}

if db_url.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}
else:
    engine_args["pool_pre_ping"] = True
    engine_args["pool_size"] = 10
    engine_args["max_overflow"] = 20

try:
    engine = create_engine(db_url, **engine_args)
    # Test connection immediately
    with engine.connect() as conn:
        logger.info("Successfully connected to the primary PostgreSQL database.")
except Exception as e:
    logger.warning(
        f"Failed to connect to primary database at {db_url} due to: {e}. "
        f"Falling back to local SQLite database: sqlite:///./kavalar.db"
    )
    # Fallback engine using SQLite
    db_url = "sqlite:///./kavalar.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

# Create SessionLocal session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency injector for database sessions.
    Ensures sessions are properly closed after the request lifecycle.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()
