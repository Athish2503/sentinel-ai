import uuid
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from app.models.session import Session
from app.schemas.session import SessionCreate, SessionUpdate

def create_session(db: DBSession, session_in: SessionCreate) -> Session:
    """
    Creates a new agent behavior session.
    """
    db_session = Session(
        prompt=session_in.prompt,
        status="pending",
        anomaly_score=0.0
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session(db: DBSession, session_id: uuid.UUID) -> Optional[Session]:
    """
    Retrieves a session by UUID.
    """
    return db.query(Session).filter(Session.id == session_id).first()

def get_sessions(db: DBSession, skip: int = 0, limit: int = 100) -> List[Session]:
    """
    Lists sessions with offset and limit pagination.
    """
    return db.query(Session).offset(skip).limit(limit).all()

def update_session(db: DBSession, db_session: Session, session_in: SessionUpdate) -> Session:
    """
    Updates the status or anomaly score of an existing session.
    """
    if session_in.anomaly_score is not None:
        db_session.anomaly_score = session_in.anomaly_score
    if session_in.status is not None:
        db_session.status = session_in.status
        
    db.commit()
    db.refresh(db_session)
    return db_session
