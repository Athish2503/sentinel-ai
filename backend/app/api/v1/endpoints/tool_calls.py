import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.tool_call import ToolCallCreate, ToolCallResponse
from app.services import tool_call as tool_call_service
from app.services import session as session_service
from app.middleware.exception_handler import EntityNotFoundException

router = APIRouter()

@router.post("/", response_model=ToolCallResponse, status_code=status.HTTP_201_CREATED)
def create_tool_call(tool_call_in: ToolCallCreate, db: Session = Depends(get_db)):
    """
    Records a tool call for a session.
    """
    # Verify the session exists
    db_session = session_service.get_session(db, tool_call_in.session_id)
    if not db_session:
        raise EntityNotFoundException("Session", str(tool_call_in.session_id))
    return tool_call_service.create_tool_call(db, tool_call_in)

@router.get("/session/{session_id}", response_model=List[ToolCallResponse])
def get_tool_calls_for_session(session_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieves all tool calls recorded in a given session, ordered by execution order.
    """
    # Verify the session exists
    db_session = session_service.get_session(db, session_id)
    if not db_session:
        raise EntityNotFoundException("Session", str(session_id))
    return tool_call_service.get_tool_calls_for_session(db, session_id)
