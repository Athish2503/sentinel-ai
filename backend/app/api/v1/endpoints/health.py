from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import get_db
from app.utils.logger import logger

router = APIRouter()

@router.get("/health")
def get_health():
    """
    Liveness probe. Indicates if the application is running.
    """
    return {
        "status": "healthy"
    }

@router.get("/readiness")
def get_readiness():
    """
    Readiness probe. Indicates if the application is ready to accept traffic.
    """
    return {
        "status": "ready"
    }

@router.get("/db-check")
def check_db_connectivity(db: Session = Depends(get_db)):
    """
    Database connectivity probe. Validates database connectivity by running a test query.
    """
    try:
        # Run a simple query to verify postgres is reachable
        db.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "message": "Successfully reached the database."
        }
    except Exception as e:
        logger.error(f"Database connectivity check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity failed: {str(e)}"
        )
