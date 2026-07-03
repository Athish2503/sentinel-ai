import uuid
from typing import List
from sqlalchemy.orm import Session as DBSession
from app.models.tool_call import ToolCall
from app.schemas.tool_call import ToolCallCreate

def create_tool_call(db: DBSession, tool_call_in: ToolCallCreate) -> ToolCall:
    """
    Records a new tool invocation for a session.
    """
    db_tool_call = ToolCall(
        session_id=tool_call_in.session_id,
        tool_name=tool_call_in.tool_name,
        tool_arguments=tool_call_in.tool_arguments,
        execution_order=tool_call_in.execution_order,
        execution_time=tool_call_in.execution_time
    )
    db.add(db_tool_call)
    db.commit()
    db.refresh(db_tool_call)
    return db_tool_call

def get_tool_calls_for_session(db: DBSession, session_id: uuid.UUID) -> List[ToolCall]:
    """
    Retrieves all tool calls registered in a specific session, sorted by execution order.
    """
    return db.query(ToolCall).filter(
        ToolCall.session_id == session_id
    ).order_by(ToolCall.execution_order).all()
