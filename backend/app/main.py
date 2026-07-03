from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.utils.config import settings
from app.utils.logger import logger
from app.database.session import engine
from app.models import Base
from app.middleware.exception_handler import register_exception_handlers
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for the application lifecycle.
    Triggers database schema synchronization on startup.
    """
    logger.info("Starting up Sentinel AI FastAPI application.")
    try:
        # Create tables automatically on startup
        logger.info("Syncing database schema (creating tables if not exists)...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema sync complete.")
    except Exception as e:
        logger.error(f"Error during startup database initialization: {e}", exc_info=True)
        # We don't crash startup immediately so health/readiness endpoints can still report errors
    
    yield
    
    logger.info("Shutting down Sentinel AI FastAPI application.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Sentinel AI: Behavioral anomaly detector for prompt injection attacks.",
    version="1.0.0",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register centralized exception handlers
register_exception_handlers(app)

# Register v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)
