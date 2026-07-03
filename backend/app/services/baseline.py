from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from app.models.baseline import Baseline
from app.schemas.baseline import BaselineCreate

def create_baseline(db: DBSession, baseline_in: BaselineCreate) -> Baseline:
    """
    Saves a newly trained behavioral baseline profile.
    """
    db_baseline = Baseline(
        model_version=baseline_in.model_version,
        training_runs=baseline_in.training_runs,
        threshold=baseline_in.threshold
    )
    db.add(db_baseline)
    db.commit()
    db.refresh(db_baseline)
    return db_baseline

def get_active_baseline(db: DBSession) -> Optional[Baseline]:
    """
    Gets the active (latest generated) behavioral baseline.
    """
    return db.query(Baseline).order_by(Baseline.created_at.desc()).first()

def get_baselines(db: DBSession, skip: int = 0, limit: int = 100) -> List[Baseline]:
    """
    Lists baseline models with pagination.
    """
    return db.query(Baseline).offset(skip).limit(limit).all()
