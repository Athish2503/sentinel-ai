from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from app.database.session import get_db
from app.services import session as session_service
from app.schemas.session import SessionCreate, SessionUpdate
from app.agents.enterprise_agent import agent_graph
from app.utils.logger import logger

class AgentRunInput(BaseModel):
    prompt: str

class AgentRunOutput(BaseModel):
    response: str
    session_id: str

router = APIRouter()

@router.post("/run", response_model=AgentRunOutput, status_code=status.HTTP_200_OK)
def run_agent(payload: AgentRunInput, db: DBSession = Depends(get_db)):
    """
    Executes the LangGraph enterprise assistant agent on a user prompt.
    Automatically initializes a behavioral logging session.
    """
    logger.info(f"Received agent run request with prompt: '{payload.prompt}'")
    
    # 1. Create a session in the database with pending status
    try:
        db_session = session_service.create_session(
            db=db,
            session_in=SessionCreate(prompt=payload.prompt)
        )
    except Exception as e:
        logger.error(f"Failed to create agent session record in DB: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize database session context: {str(e)}"
        )
        
    session_id_str = str(db_session.id)
    logger.info(f"Successfully initialized session {session_id_str} for prompt.")

    # 2. Invoke the compiled LangGraph agent graph
    # Config is used to pass the session_id to tool executions
    config = {
        "configurable": {
            "session_id": session_id_str
        }
    }
    
    try:
        # Run agent
        result = agent_graph.invoke(
            {"messages": [HumanMessage(content=payload.prompt)]},
            config=config
        )
        
        # 3. Retrieve agent's response
        messages = result.get("messages", [])
        if not messages:
            raise ValueError("Agent graph returned an empty message trajectory.")
            
        final_message = messages[-1]
        response_content = final_message.content
        
        # Update session status to completed
        session_service.update_session(
            db=db,
            db_session=db_session,
            session_in=SessionUpdate(status="completed")
        )
        logger.info(f"Agent execution completed successfully for session {session_id_str}.")
        
        return AgentRunOutput(
            response=response_content,
            session_id=session_id_str
        )
        
    except Exception as e:
        logger.error(f"Error occurred during agent execution for session {session_id_str}: {e}", exc_info=True)
        # Update session status to failed
        try:
            session_service.update_session(
                db=db,
                db_session=db_session,
                session_in=SessionUpdate(status="failed")
            )
        except Exception as db_update_err:
            logger.error(f"Failed to update session status to failed: {db_update_err}", exc_info=True)
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failed: {str(e)}"
        )
