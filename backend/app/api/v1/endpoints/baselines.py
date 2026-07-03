from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.baseline import BaselineCreate, BaselineResponse
from app.services import baseline as baseline_service
from app.middleware.exception_handler import EntityNotFoundException

router = APIRouter()

@router.post("/", response_model=BaselineResponse, status_code=status.HTTP_201_CREATED)
def create_baseline(baseline_in: BaselineCreate, db: Session = Depends(get_db)):
    """
    Creates/saves a new behavioral baseline profile.
    """
    return baseline_service.create_baseline(db, baseline_in)

@router.get("/", response_model=List[BaselineResponse])
def get_baselines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lists baseline profiles.
    """
    return baseline_service.get_baselines(db, skip=skip, limit=limit)

@router.get("/active", response_model=BaselineResponse)
def get_active_baseline(db: Session = Depends(get_db)):
    """
    Retrieves the active baseline profile (the latest saved).
    """
    active_baseline = baseline_service.get_active_baseline(db)
    if not active_baseline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active baseline has been established yet."
        )
    
    # Calculate stats dynamically from feature vectors
    stats = baseline_service.calculate_baseline_stats(active_baseline.feature_vectors)
    active_baseline.statistics = stats
    
    return active_baseline
