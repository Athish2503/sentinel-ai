import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sklearn.ensemble import IsolationForest
import numpy as np

from app.models.baseline import Baseline, BaselineFeatureVector
from app.detector.feature_extractor import FeatureExtractor
from app.detector.behavior_vector import BehaviorVector
from app.detector.trainer import IsolationForestTrainer
from app.utils.logger import logger

class IsolationForestPredictor:
    """
    Handles predicting anomaly scores for target sessions by automatically loading,
    training, and caching the Isolation Forest model from the active database baseline.
    """
    
    _cached_baseline_id: Optional[uuid.UUID] = None
    _cached_model: Optional[IsolationForest] = None
    _cached_vocabulary: Optional[List[str]] = None
    _cached_baseline_vectors: Optional[List[Dict[str, Any]]] = None
    _cached_threshold: float = 0.0

    @classmethod
    def _load_baseline_model(cls, db: Session) -> None:
        """
        Retrieves the active baseline from database, builds the vocabulary,
        extracts behavior vectors, fits the Isolation Forest model, and caches them.
        """
        from app.services import baseline as baseline_service
        active_baseline = baseline_service.get_active_baseline(db)
        if not active_baseline:
            raise ValueError("No active baseline has been established in the database.")

        # If the cached model belongs to the current active baseline, we are good
        if cls._cached_baseline_id == active_baseline.id and cls._cached_model is not None:
            return

        logger.info(f"Loading baseline model automatically. Version: {active_baseline.model_version}, ID: {active_baseline.id}")

        # Fetch baseline feature vectors
        db_fvs = db.query(BaselineFeatureVector).filter(
            BaselineFeatureVector.baseline_id == active_baseline.id
        ).all()
        
        if not db_fvs:
            raise ValueError(f"Active baseline {active_baseline.model_version} has no training feature vectors.")

        # Build vocabulary dynamically from baseline sequence logs
        vocab_set = set()
        for fv in db_fvs:
            for tool_name in fv.sequence:
                vocab_set.add(tool_name)
        vocabulary = sorted(list(vocab_set))

        # Convert baseline feature vectors database records to features dict list
        baseline_features = []
        for fv in db_fvs:
            baseline_features.append({
                "prompt": fv.prompt,
                "sequence": fv.sequence,
                "tool_frequency": fv.tool_frequency,
                "execution_order": fv.execution_order,
                "execution_count": fv.execution_count,
                "average_execution_time": fv.average_execution_time,
                "parameter_length": fv.parameter_length
            })

        # Build behavior vectors
        behavior_vectors = [
            BehaviorVector.from_features(fv_dict, vocabulary)
            for fv_dict in baseline_features
        ]

        # Train Isolation Forest
        trainer = IsolationForestTrainer(contamination=0.01)
        model = trainer.train(behavior_vectors)

        # Cache variables
        cls._cached_baseline_id = active_baseline.id
        cls._cached_model = model
        cls._cached_vocabulary = vocabulary
        cls._cached_baseline_vectors = baseline_features
        cls._cached_threshold = active_baseline.threshold

        logger.info("Successfully loaded and cached baseline Isolation Forest model.")

    @classmethod
    def predict(cls, db: Session, session_id: uuid.UUID) -> Dict[str, Any]:
        """
        Loads baseline model if needed, extracts features for the target session,
        computes anomaly score, determines status, and returns detection details.
        """
        # Ensure baseline is loaded and up to date
        cls._load_baseline_model(db)

        # Extract features from target session
        session_features = FeatureExtractor.extract_from_db(db, session_id)

        # Build behavior vector using the cached vocabulary
        session_bv = BehaviorVector.from_features(session_features, cls._cached_vocabulary)

        # Reshape for prediction (single sample)
        X = session_bv.to_array().reshape(1, -1)

        # Get anomaly score from model
        decision_score = cls._cached_model.decision_function(X)[0]

        # Convert to continuous anomaly score between 0 and 1
        # Use sigmoid scaling to map:
        # decision_score <= 0 (anomalous) maps to score >= 0.5
        # decision_score > 0 (normal) maps to score < 0.5
        score = float(1.0 / (1.0 + np.exp(decision_score * 10.0)))

        # Determine status: if decision_score < baseline threshold (which is 0.0 by default)
        is_anomaly = decision_score < cls._cached_threshold
        status = "Injected" if is_anomaly else "Normal"

        # Hybrid detection: Check for high-confidence rule-based anomalies to override false negatives
        from app.detector.explainer import BehaviorExplainer
        reasons = BehaviorExplainer.explain(
            session_features=session_features,
            baseline_features=cls._cached_baseline_vectors,
            vocabulary=cls._cached_vocabulary
        )
        
        has_unusual_transitions = False
        has_unexpected_tools = False
        has_excessive_count = False
        has_suspicious_payload = False
        
        for reason in reasons:
            if "unusual tool transitions" in reason:
                has_unusual_transitions = True
            if "Unexpected tool usage" in reason:
                has_unexpected_tools = True
            if "Unusual execution count" in reason:
                # Flag as high-confidence if count is significantly high (e.g. >= 4)
                if session_features.get("execution_count", 0) >= 4:
                    has_excessive_count = True
            if "suspicious patterns" in reason:
                has_suspicious_payload = True
                
        is_high_confidence_anomaly = (
            has_unusual_transitions or 
            has_unexpected_tools or 
            has_excessive_count or 
            has_suspicious_payload
        )
        
        if is_high_confidence_anomaly:
            status = "Injected"
            if score < 0.5:
                score = 0.5 + (0.4 * (1.0 - score))  # Boost score to 0.5 - 0.9 range

        return {
            "score": score,
            "decision_score": decision_score,
            "status": status,
            "session_features": session_features,
            "vocabulary": cls._cached_vocabulary,
            "baseline_features": cls._cached_baseline_vectors
        }
