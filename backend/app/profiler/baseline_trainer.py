import uuid
import time
import random
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
import numpy as np

from sqlalchemy.orm import Session as DBSession
from langchain_core.messages import HumanMessage

from app.models.session import Session as DBASession
from app.models.tool_call import ToolCall
from app.models.baseline import Baseline, BaselineFeatureVector
from app.agents.enterprise_agent import agent_graph
from app.tools.agent_tools import (
    search_documents,
    read_document,
    calculator,
    send_email,
    lookup_customer
)
from app.utils.logger import logger
from app.utils.config import settings

NORMAL_PROMPTS = [
    # Summarize employee handbook
    "Please summarize the main policies in the employee handbook.",
    "Can you provide a summary of the employee handbook?",
    "Summarize the working hours and standards from the employee handbook.",
    "What are the core hours listed in the employee handbook? Summarize them.",
    "Read the employee handbook and give me a brief summary of standard annual leave.",
    # Find travel policy
    "Can you help me find the travel policy?",
    "Where is the travel policy document?",
    "Find the travel policy for standard lodging rates and search for it.",
    "Search the documents for anything related to travel policy.",
    "Find the enterprise travel policy guidelines.",
    # Read leave policy
    "Please read the leave policy for me.",
    "Search for the leave policy and summarize standard annual leave days.",
    "Read the leave policy to find the standard annual leave count.",
    "Find the leave policy document and read its details.",
    "What does the leave policy say about standard annual leave?",
    # Lookup customer information
    "Lookup customer information for Bob Smith.",
    "Could you look up the customer record for customer cust_101?",
    "Check customer information for customer cust_103.",
    "Get customer details for customer cust_102.",
    "Lookup the customer profile of Alice Johnson.",
    # Calculate reimbursement
    "Calculate my total reimbursement for 150 + 200 + 45.",
    "Calculate reimbursement expenses: 120 + 80 + 350.",
    "Please calculate 250 + 75 for my travel reimbursement.",
    "Calculate 450 - 50 for the standard lodging reimbursement.",
    "What is the sum of 99.5 * 3 for my travel reimbursement?",
    # Read onboarding guide
    "Read the onboarding guide for new hires.",
    "Find and read the onboarding guide document.",
    "Search the documents for the onboarding guide.",
    "Can you open and read the onboarding guide?",
    "Lookup and summarize the onboarding guide."
]

def simulate_tools_for_prompt(prompt: str, config: dict):
    """
    Simulates the agent run tool call invocations for a predefined normal prompt.
    Invokes tools using their .invoke method, which runs middleware and logs tool calls to the database.
    """
    prompt_lower = prompt.lower()
    
    # 1. Summarize employee handbook
    if "employee handbook" in prompt_lower:
        time.sleep(random.uniform(0.01, 0.03))
        search_documents.invoke({"query": "employee handbook"}, config=config)
        time.sleep(random.uniform(0.01, 0.03))
        read_document.invoke({"doc_id": "doc_2"}, config=config)
        
    # 2. Read leave policy
    elif "leave policy" in prompt_lower:
        time.sleep(random.uniform(0.01, 0.03))
        search_documents.invoke({"query": "leave policy"}, config=config)
        time.sleep(random.uniform(0.01, 0.03))
        read_document.invoke({"doc_id": "doc_2"}, config=config)
        
    # 3. Find travel policy
    elif "travel policy" in prompt_lower or "travel" in prompt_lower:
        time.sleep(random.uniform(0.01, 0.03))
        search_documents.invoke({"query": "travel policy"}, config=config)
        
    # 4. Lookup customer information
    elif "customer" in prompt_lower or "bob smith" in prompt_lower or "alice johnson" in prompt_lower:
        customer_id = "cust_101"
        if "cust_102" in prompt_lower:
            customer_id = "cust_102"
        elif "cust_103" in prompt_lower:
            customer_id = "cust_103"
        elif "bob smith" in prompt_lower:
            customer_id = "cust_102"
        elif "charlie brown" in prompt_lower:
            customer_id = "cust_103"
        time.sleep(random.uniform(0.01, 0.03))
        lookup_customer.invoke({"customer_id": customer_id}, config=config)
        
    # 5. Calculate reimbursement / calculator
    elif "calculate" in prompt_lower or "sum of" in prompt_lower:
        expression = "150 + 200 + 45"
        if "120 + 80 + 350" in prompt_lower:
            expression = "120 + 80 + 350"
        elif "250 + 75" in prompt_lower:
            expression = "250 + 75"
        elif "450 - 50" in prompt_lower:
            expression = "450 - 50"
        elif "99.5 * 3" in prompt_lower:
            expression = "99.5 * 3"
        time.sleep(random.uniform(0.01, 0.03))
        calculator.invoke({"expression": expression}, config=config)
        
    # 6. Read onboarding guide
    elif "onboarding" in prompt_lower:
        time.sleep(random.uniform(0.01, 0.03))
        search_documents.invoke({"query": "onboarding guide"}, config=config)
        
    # Default fallback
    else:
        time.sleep(random.uniform(0.01, 0.03))
        search_documents.invoke({"query": "general inquiry"}, config=config)

def extract_features(db: DBSession, session_id: uuid.UUID, prompt: str) -> Dict[str, Any]:
    """
    Queries and extracts feature vector values from the ToolCall logs of a session.
    """
    tool_calls = db.query(ToolCall).filter(ToolCall.session_id == session_id).order_by(ToolCall.execution_order).all()
    
    sequence = [tc.tool_name for tc in tool_calls]
    
    tool_frequency = {}
    for name in sequence:
        tool_frequency[name] = tool_frequency.get(name, 0) + 1
        
    execution_order = sequence
    execution_count = len(tool_calls)
    
    avg_execution_time = 0.0
    if execution_count > 0:
        avg_execution_time = sum(tc.execution_time for tc in tool_calls) / execution_count
        
    # Parameter length is the sum of lengths of stringified JSON objects of tool arguments
    parameter_length = sum(len(json.dumps(tc.tool_arguments)) for tc in tool_calls)
    
    return {
        "prompt": prompt,
        "sequence": sequence,
        "tool_frequency": tool_frequency,
        "execution_order": execution_order,
        "execution_count": execution_count,
        "average_execution_time": avg_execution_time,
        "parameter_length": parameter_length
    }

def train_baseline(db: DBSession, num_runs: int = 25, use_real_agent: bool = False) -> Tuple[Baseline, Dict[str, Any]]:
    """
    Generates 20-30 normal agent runs, collects feature vectors, stores them, and returns statistics.
    """
    logger.info(f"Starting baseline training. Runs: {num_runs}, Real Agent: {use_real_agent}")
    
    # Ensure num_runs is within bounds 20-30 if not specified otherwise
    if num_runs < 20:
        num_runs = 20
    elif num_runs > 30:
        num_runs = 30
        
    # Sample or select prompts
    prompts_to_use = NORMAL_PROMPTS.copy()
    if num_runs < len(prompts_to_use):
        prompts_to_use = random.sample(prompts_to_use, num_runs)
    elif num_runs > len(prompts_to_use):
        # Repeat prompts if requested more than the unique ones available
        prompts_to_use = (prompts_to_use * (num_runs // len(prompts_to_use) + 1))[:num_runs]
        
    feature_vectors_data = []
    
    # Create baseline configuration record
    model_version = f"v{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    db_baseline = Baseline(
        model_version=model_version,
        training_runs=num_runs,
        threshold=0.0 # Anomaly detection threshold not implemented yet
    )
    db.add(db_baseline)
    db.commit()
    db.refresh(db_baseline)
    
    for i, prompt in enumerate(prompts_to_use):
        logger.info(f"Running baseline training execution {i+1}/{num_runs} for prompt: '{prompt}'")
        
        # Create session record
        session = DBASession(prompt=prompt, status="pending")
        db.add(session)
        db.commit()
        db.refresh(session)
        
        session_id_str = str(session.id)
        config = {
            "configurable": {
                "session_id": session_id_str
            }
        }
        
        try:
            if use_real_agent:
                if not settings.GROQ_API_KEY:
                    raise ValueError("GROQ_API_KEY env var is missing. Cannot train baseline using a real agent.")
                
                # Invoke the LangGraph agent
                agent_graph.invoke(
                    {"messages": [HumanMessage(content=prompt)]},
                    config=config
                )
            else:
                # Simulated run
                simulate_tools_for_prompt(prompt, config)
                
            # Update session status
            session.status = "completed"
            db.commit()
            
            # Extract features
            fv = extract_features(db, session.id, prompt)
            feature_vectors_data.append((session.id, fv))
            
        except Exception as e:
            logger.error(f"Error during training run {i+1} for prompt '{prompt}': {e}", exc_info=True)
            session.status = "failed"
            db.commit()
            raise e
            
    # Store all feature vectors in DB
    stored_fvs = []
    for s_id, fv in feature_vectors_data:
        db_fv = BaselineFeatureVector(
            baseline_id=db_baseline.id,
            session_id=s_id,
            prompt=fv["prompt"],
            sequence=fv["sequence"],
            tool_frequency=fv["tool_frequency"],
            execution_order=fv["execution_order"],
            execution_count=fv["execution_count"],
            average_execution_time=fv["average_execution_time"],
            parameter_length=fv["parameter_length"]
        )
        db.add(db_fv)
        stored_fvs.append(db_fv)
        
    db.commit()
    
    # Calculate statistics describing the learned baseline
    execution_counts = [fv["execution_count"] for _, fv in feature_vectors_data]
    execution_times = []
    parameter_lengths = []
    all_tools_used = set()
    global_tool_frequencies = {}
    sequences_frequency = {}
    
    for _, fv in feature_vectors_data:
        for tool in fv["sequence"]:
            all_tools_used.add(tool)
            global_tool_frequencies[tool] = global_tool_frequencies.get(tool, 0) + 1
            
        execution_times.append(fv["average_execution_time"])
        parameter_lengths.append(fv["parameter_length"])
        
        seq_str = ",".join(fv["sequence"]) if fv["sequence"] else "None"
        sequences_frequency[seq_str] = sequences_frequency.get(seq_str, 0) + 1
        
    avg_execution_count = float(np.mean(execution_counts)) if execution_counts else 0.0
    max_execution_count = int(np.max(execution_counts)) if execution_counts else 0
    avg_execution_time = float(np.mean(execution_times)) if execution_times else 0.0
    avg_parameter_length = float(np.mean(parameter_lengths)) if parameter_lengths else 0.0
    
    statistics = {
        "total_runs": num_runs,
        "unique_tools_used": list(all_tools_used),
        "tool_frequencies": global_tool_frequencies,
        "avg_execution_count_per_run": avg_execution_count,
        "max_execution_count_per_run": max_execution_count,
        "avg_execution_time": avg_execution_time,
        "avg_parameter_length": avg_parameter_length,
        "sequences_frequency": sequences_frequency
    }
    
    logger.info(f"Successfully trained baseline profile '{model_version}' with ID: {db_baseline.id}")
    return db_baseline, statistics
