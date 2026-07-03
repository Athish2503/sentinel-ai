import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.session import SessionCreate, SessionResponse, SessionUpdate
from app.services import session as session_service
from app.middleware.exception_handler import EntityNotFoundException

router = APIRouter()

@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_in: SessionCreate, db: Session = Depends(get_db)):
    """
    Creates a new behavioral monitoring session.
    """
    return session_service.create_session(db, session_in)

@router.get("/", response_model=List[SessionResponse])
def get_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lists all recorded sessions.
    """
    return session_service.get_sessions(db, skip=skip, limit=limit)

@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieves details for a specific session.
    """
    db_session = session_service.get_session(db, session_id)
    if not db_session:
        raise EntityNotFoundException("Session", str(session_id))
    return db_session

@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(session_id: uuid.UUID, session_in: SessionUpdate, db: Session = Depends(get_db)):
    """
    Updates an existing session's parameters (e.g. status or anomaly score).
    """
    db_session = session_service.get_session(db, session_id)
    if not db_session:
        raise EntityNotFoundException("Session", str(session_id))
    return session_service.update_session(db, db_session, session_in)
