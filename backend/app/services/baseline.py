from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session as DBSession
from app.models.baseline import Baseline
from app.schemas.baseline import BaselineCreate
from app.utils.logger import logger

def calculate_baseline_stats(feature_vectors: List[Any]) -> Dict[str, Any]:
    """
    Dynamically compiles statistics (frequencies, averages, transitions) from baseline feature vectors.
    """
    if not feature_vectors:
        return {
            "total_runs": 0,
            "unique_tools_used": [],
            "tool_frequencies": {},
            "avg_execution_count_per_run": 0.0,
            "max_execution_count_per_run": 0,
            "avg_execution_time": 0.0,
            "avg_parameter_length": 0.0,
            "sequences_frequency": {}
        }
    
    import numpy as np
    execution_counts = [fv.execution_count for fv in feature_vectors]
    execution_times = []
    parameter_lengths = []
    all_tools_used = set()
    global_tool_frequencies = {}
    sequences_frequency = {}
    
    for fv in feature_vectors:
        seq = fv.sequence or []
        for tool in seq:
            all_tools_used.add(tool)
            global_tool_frequencies[tool] = global_tool_frequencies.get(tool, 0) + 1
            
        execution_times.append(fv.average_execution_time)
        parameter_lengths.append(fv.parameter_length)
        
        seq_str = ",".join(seq) if seq else "None"
        sequences_frequency[seq_str] = sequences_frequency.get(seq_str, 0) + 1
        
    avg_execution_count = float(np.mean(execution_counts)) if execution_counts else 0.0
    max_execution_count = int(np.max(execution_counts)) if execution_counts else 0
    avg_execution_time = float(np.mean(execution_times)) if execution_times else 0.0
    avg_parameter_length = float(np.mean(parameter_lengths)) if parameter_lengths else 0.0
    
    return {
        "total_runs": len(feature_vectors),
        "unique_tools_used": list(all_tools_used),
        "tool_frequencies": global_tool_frequencies,
        "avg_execution_count_per_run": avg_execution_count,
        "max_execution_count_per_run": max_execution_count,
        "avg_execution_time": avg_execution_time,
        "avg_parameter_length": avg_parameter_length,
        "sequences_frequency": sequences_frequency
    }

def create_baseline(db: DBSession, baseline_in: BaselineCreate) -> Baseline:
    """
    Saves a newly trained behavioral baseline profile.
    """
    db_baseline = Baseline(
        model_version=baseline_in.model_version,
        training_runs=baseline_in.training_runs,
        threshold=baseline_in.threshold
    )
    db.add(db_baseline)
    db.commit()
    db.refresh(db_baseline)
    return db_baseline

def get_active_baseline(db: DBSession) -> Optional[Baseline]:
    """
    Gets the active (latest generated) behavioral baseline.
    If no baseline is established, auto-trains a default local baseline to self-heal.
    """
    baseline = db.query(Baseline).order_by(Baseline.created_at.desc()).first()
    if not baseline:
        logger.info("No active baseline established yet. Self-healing: training a default baseline...")
        try:
            from app.profiler.baseline_trainer import train_baseline
            baseline, _ = train_baseline(db, num_runs=20, use_real_agent=False)
            logger.info(f"Self-healing complete. Successfully trained active baseline: {baseline.model_version}")
        except Exception as e:
            logger.error(f"Failed to auto-train fallback baseline: {e}", exc_info=True)
            return None
    return baseline

def get_baselines(db: DBSession, skip: int = 0, limit: int = 100) -> List[Baseline]:
    """
    Lists baseline models with pagination.
    """
    return db.query(Baseline).offset(skip).limit(limit).all()
