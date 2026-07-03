import json
import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.tool_call import ToolCall
from app.models.session import Session as DBSessionModel

class FeatureExtractor:
    """
    Extracts behavioral features from agent session tool calls for anomaly detection.
    """

    @staticmethod
    def extract_from_db(db: Session, session_id: uuid.UUID) -> Dict[str, Any]:
        """
        Queries tool calls and prompt for a session from the DB and extracts raw features.
        """
        session_record = db.query(DBSessionModel).filter(DBSessionModel.id == session_id).first()
        prompt = session_record.prompt if session_record else ""
        
        tool_calls = db.query(ToolCall).filter(
            ToolCall.session_id == session_id
        ).order_by(ToolCall.execution_order).all()
        
        return FeatureExtractor.extract_from_tool_calls(tool_calls, prompt)

    @staticmethod
    def extract_from_tool_calls(tool_calls: List[ToolCall], prompt: str) -> Dict[str, Any]:
        """
        Extracts features from a list of ToolCall models.
        """
        sequence = [tc.tool_name for tc in tool_calls]
        
        tool_frequency = {}
        for name in sequence:
            tool_frequency[name] = tool_frequency.get(name, 0) + 1
            
        execution_count = len(tool_calls)
        
        avg_execution_time = 0.0
        if execution_count > 0:
            avg_execution_time = sum(tc.execution_time for tc in tool_calls) / execution_count
            
        parameter_length = 0
        for tc in tool_calls:
            if tc.tool_arguments is not None:
                if isinstance(tc.tool_arguments, dict):
                    parameter_length += len(json.dumps(tc.tool_arguments))
                elif isinstance(tc.tool_arguments, str):
                    parameter_length += len(tc.tool_arguments)
                else:
                    parameter_length += len(str(tc.tool_arguments))
                
        return {
            "prompt": prompt,
            "sequence": sequence,
            "tool_frequency": tool_frequency,
            "execution_order": sequence,
            "execution_count": execution_count,
            "average_execution_time": avg_execution_time,
            "parameter_length": parameter_length
        }
