from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.database.session import get_db
from app.schemas.baseline import BaselineTrainRequest, BaselineTrainResponse
from app.profiler import baseline_trainer

router = APIRouter()

@router.post("/train", response_model=BaselineTrainResponse, status_code=status.HTTP_201_CREATED)
def train_baseline_profile(
    payload: BaselineTrainRequest = BaselineTrainRequest(),
    db: DBSession = Depends(get_db)
):
    """
    Triggers baseline model training.
    Generates 20-30 normal agent runs using predefined prompts,
    collects and stores feature vectors, and returns learned statistics.
    """
    try:
        baseline, stats = baseline_trainer.train_baseline(
            db=db,
            num_runs=payload.num_runs,
            use_real_agent=payload.use_real_agent
        )
        
        # Build response explicitly matching BaselineTrainResponse
        return BaselineTrainResponse(
            baseline_id=baseline.id,
            model_version=baseline.model_version,
            training_runs=baseline.training_runs,
            threshold=baseline.threshold,
            created_at=baseline.created_at,
            statistics=stats,
            feature_vectors=baseline.feature_vectors
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Baseline training execution failed: {str(e)}"
        )
