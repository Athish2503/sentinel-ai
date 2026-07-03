from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.database.session import get_db
from app.schemas.detect import DetectRequest, DetectResponse
from app.schemas.session import SessionUpdate
from app.schemas.alert import AlertCreate
from app.services import session as session_service
from app.services import alert as alert_service
from app.detector import IsolationForestPredictor, BehaviorExplainer
from app.utils.logger import logger

router = APIRouter()

@router.post("/detect", response_model=DetectResponse, status_code=status.HTTP_200_OK)
def detect_anomalies(payload: DetectRequest, db: DBSession = Depends(get_db)):
    """
    Evaluates an agent execution session for behavioral anomalies using a trained baseline.
    Logs anomaly score and status, creates alerts if malicious behavior is detected.
    """
    logger.info(f"Received anomaly detection request for session: {payload.session_id}")
    
    # 1. Fetch the session record
    db_session = session_service.get_session(db, payload.session_id)
    if not db_session:
        logger.warning(f"Session {payload.session_id} not found in database.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID '{payload.session_id}' not found."
        )
        
    # 2. Run Isolation Forest prediction
    try:
        prediction = IsolationForestPredictor.predict(db, db_session.id)
    except ValueError as val_err:
        logger.error(f"Prediction failed for session {payload.session_id}: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as e:
        logger.error(f"Anomaly detection failed for session {payload.session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Anomaly detection failed: {str(e)}"
        )
        
    # 3. Generate explanations
    reasons = BehaviorExplainer.explain(
        session_features=prediction["session_features"],
        baseline_features=prediction["baseline_features"],
        vocabulary=prediction["vocabulary"]
    )
    
    # Ensure reasons is populated if status is Injected
    if prediction["status"] == "Injected" and not reasons:
        reasons.append("Behavioral anomaly: Isolation Forest model detected general execution flow deviation from established baseline.")
        
    score = prediction["score"]
    status_label = prediction["status"]
    
    # 4. Update the session record in DB
    try:
        session_service.update_session(
            db=db,
            db_session=db_session,
            session_in=SessionUpdate(
                anomaly_score=score,
                status=status_label
            )
        )
        logger.info(f"Updated session {db_session.id} with score {score:.4f} and status '{status_label}'")
    except Exception as db_err:
        logger.error(f"Failed to update session {db_session.id} in database: {db_err}", exc_info=True)
        # We don't crash here since detection succeeded, but we log the error
        
    # 5. Create alert in database if anomaly is detected
    if status_label == "Injected":
        try:
            alert_reason = "\n".join([f"* {r}" for r in reasons]) if len(reasons) > 1 else (reasons[0] if reasons else "Behavioral anomaly")
            alert_in = AlertCreate(
                session_id=db_session.id,
                score=score,
                reason=alert_reason
            )
            alert_rec = alert_service.create_alert(db, alert_in)
            logger.info(f"Triggered anomaly alert {alert_rec.id} for session {db_session.id}")
        except Exception as alert_err:
            logger.error(f"Failed to create alert for session {db_session.id}: {alert_err}", exc_info=True)
            
    # 6. Return response
    return DetectResponse(
        score=score,
        status=status_label,
        reasons=reasons
    )
