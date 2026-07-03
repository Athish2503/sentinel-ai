import uuid
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from app.models.alert import Alert
from app.schemas.alert import AlertCreate

def create_alert(db: DBSession, alert_in: AlertCreate) -> Alert:
    """
    Creates a new security alert for a suspicious session.
    """
    db_alert = Alert(
        session_id=alert_in.session_id,
        score=alert_in.score,
        reason=alert_in.reason
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_alert(db: DBSession, alert_id: uuid.UUID) -> Optional[Alert]:
    """
    Retrieves an alert by its ID.
    """
    return db.query(Alert).filter(Alert.id == alert_id).first()

def get_alerts(db: DBSession, skip: int = 0, limit: int = 100) -> List[Alert]:
    """
    Lists alerts with pagination.
    """
    return db.query(Alert).order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()

def get_alerts_for_session(db: DBSession, session_id: uuid.UUID) -> List[Alert]:
    """
    Gets all alerts linked to a session.
    """
    return db.query(Alert).filter(Alert.session_id == session_id).all()
