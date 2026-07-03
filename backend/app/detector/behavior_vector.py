import numpy as np
from typing import List, Dict, Any

class BehaviorVector:
    """
    Represents the numerical feature vector of an agent session, ready for Isolation Forest.
    """
    
    def __init__(
        self,
        execution_count: float,
        average_execution_time: float,
        parameter_length: float,
        tool_counts: List[float],
        unexpected_tool_count: float
    ):
        self.execution_count = execution_count
        self.average_execution_time = average_execution_time
        self.parameter_length = parameter_length
        self.tool_counts = tool_counts
        self.unexpected_tool_count = unexpected_tool_count

    def to_array(self) -> np.ndarray:
        """
        Converts the features to a flat 1D numpy array.
        """
        return np.array([
            self.execution_count,
            self.average_execution_time,
            self.parameter_length,
            *self.tool_counts,
            self.unexpected_tool_count
        ], dtype=np.float64)

    @classmethod
    def from_features(cls, features: Dict[str, Any], vocabulary: List[str]) -> "BehaviorVector":
        """
        Constructs a BehaviorVector from raw features dict and a baseline tool vocabulary.
        """
        exec_count = float(features.get("execution_count", 0))
        avg_exec_time = float(features.get("average_execution_time", 0.0))
        param_len = float(features.get("parameter_length", 0))
        
        tool_freq = features.get("tool_frequency", {})
        
        tool_counts = []
        unexpected_tool_count = 0.0
        
        # Build frequency features for expected vocabulary tools
        vocab_set = set(vocabulary)
        for tool_name in vocabulary:
            tool_counts.append(float(tool_freq.get(tool_name, 0)))
            
        # Sum the frequency of any tools not in vocabulary (unexpected tools)
        for tool_name, count in tool_freq.items():
            if tool_name not in vocab_set:
                unexpected_tool_count += float(count)
                
        return cls(
            execution_count=exec_count,
            average_execution_time=avg_exec_time,
            parameter_length=param_len,
            tool_counts=tool_counts,
            unexpected_tool_count=unexpected_tool_count
        )
