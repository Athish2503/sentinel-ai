import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.alert import AlertCreate, AlertResponse
from app.services import alert as alert_service
from app.services import session as session_service
from app.middleware.exception_handler import EntityNotFoundException

router = APIRouter()

@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(alert_in: AlertCreate, db: Session = Depends(get_db)):
    """
    Creates/triggers a new anomaly alert.
    """
    # Verify the session exists
    db_session = session_service.get_session(db, alert_in.session_id)
    if not db_session:
        raise EntityNotFoundException("Session", str(alert_in.session_id))
    return alert_service.create_alert(db, alert_in)

@router.get("/", response_model=List[AlertResponse])
def get_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lists triggered alerts.
    """
    return alert_service.get_alerts(db, skip=skip, limit=limit)

@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieves a specific alert's details.
    """
    db_alert = alert_service.get_alert(db, alert_id)
    if not db_alert:
        raise EntityNotFoundException("Alert", str(alert_id))
    return db_alert

@router.get("/session/{session_id}", response_model=List[AlertResponse])
def get_alerts_for_session(session_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieves all alerts generated for a specific session.
    """
    # Verify the session exists
    db_session = session_service.get_session(db, session_id)
    if not db_session:
        raise EntityNotFoundException("Session", str(session_id))
    return alert_service.get_alerts_for_session(db, session_id)
