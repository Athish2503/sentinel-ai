from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.database.session import get_db
from app.schemas.simulate import SimulateResponse
from app.simulator import run_simulation
from app.utils.logger import logger

router = APIRouter()

@router.post("/simulate/{attack_number}", response_model=SimulateResponse, status_code=status.HTTP_200_OK)
def simulate_attack(attack_number: int, db: DBSession = Depends(get_db)):
    """
    Executes a prompt injection simulation scenario (0-3).
    - Runs the LangGraph agent using a mock LLM setup.
    - Captures behavioral tool execution metrics in the DB.
    - Evaluates the session using the Isolation Forest anomaly detector.
    - Stores the anomaly score and alerts in DB if needed.
    - Returns metrics, tool execution logs, and the explanation.
    """
    logger.info(f"Received simulation request for attack scenario: {attack_number}")
    
    if attack_number not in [0, 1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid attack number: {attack_number}. Supported scenarios are: 0 (Normal Run), 1 (Email Tool Injection), 2 (Repeated execution), 3 (Sequence deviation)."
        )
        
    try:
        results = run_simulation(db, attack_number)
        return SimulateResponse(**results)
    except ValueError as val_err:
        logger.error(f"Validation error during simulation: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        )
    except Exception as e:
        logger.error(f"Simulation of attack {attack_number} failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {str(e)}"
        )
