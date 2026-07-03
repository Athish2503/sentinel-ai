from sklearn.ensemble import IsolationForest
import numpy as np
from typing import List

from app.detector.behavior_vector import BehaviorVector

class IsolationForestTrainer:
    """
    Trains the Isolation Forest model using normal baseline behavior vectors.
    """
    
    def __init__(self, contamination: float = 0.01, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state

    def train(self, behavior_vectors: List[BehaviorVector]) -> IsolationForest:
        """
        Fits an Isolation Forest model on a set of behavior vectors.
        """
        if not behavior_vectors:
            raise ValueError("Cannot train IsolationForest on an empty list of behavior vectors.")
            
        X = np.vstack([bv.to_array() for bv in behavior_vectors])
        
        model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100
        )
        model.fit(X)
        return model
