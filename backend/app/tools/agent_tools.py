import ast
import time
import uuid
import operator
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Dict, List, Callable

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

from app.database.session import SessionLocal
from app.models.tool_call import ToolCall
from app.utils.logger import logger

# --- MOCK DATA CORPORES ---

MOCK_DOCUMENTS: Dict[str, Dict[str, str]] = {
    "doc_1": {
        "title": "Kavalar Project Charter",
        "content": "Kavalar Project Charter: We are building a state-of-the-art behavioral anomaly detector for LLM agents. Lead architect: Athish. Contact email: lead_developer@kavalar.ai. Target release date: Q4 2026."
    },
    "doc_2": {
        "title": "Employee Handbook & Policies",
        "content": "Employee Handbook: Core working hours are 10 AM to 4 PM. Standard annual leave is 25 days. Employees are required to report any suspected security anomalies to security@kavalar.ai immediately."
    },
    "doc_3": {
        "title": "Database Connection Guidelines",
        "content": "Database Policy: Direct database access is restricted. PostgreSQL credentials must be rotated every 90 days. For emergencies, contact db-admin@kavalar.ai. Never hardcode credentials in source code."
    },
    "doc_4": {
        "title": "API Gateway Configurations",
        "content": "API Gateway Docs: The external facing endpoints are managed by Kong API Gateway. Rate limits are set to 100 requests per minute per IP for public endpoints, and 1000 requests per minute for authenticated enterprise tiers."
    }
}

MOCK_CUSTOMERS: Dict[str, Dict[str, str]] = {
    "cust_101": {
        "name": "Alice Johnson",
        "email": "alice@acme.com",
        "tier": "Enterprise",
        "status": "Active"
    },
    "cust_102": {
        "name": "Bob Smith",
        "email": "bob@startup.io",
        "tier": "Free",
        "status": "Pending Verification"
    },
    "cust_103": {
        "name": "Charlie Brown",
        "email": "charlie@hq.com",
        "tier": "Pro",
        "status": "Suspended"
    }
}

# --- SAFE CALCULATOR EVALUATOR ---

# Safe mathematical operators
MATH_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: lambda x: x
}

def eval_expr(expr: str) -> str:
    """
    Safely parses and evaluates mathematical expression using Python AST.
    """
    try:
        clean_expr = expr.strip().replace(" ", "")
        node = ast.parse(clean_expr, mode='eval')
        
        def _eval(n):
            if isinstance(n, ast.Expression):
                return _eval(n.body)
            elif isinstance(n, ast.Constant):  # Python >= 3.8
                return n.value
            elif hasattr(ast, "Num") and isinstance(n, getattr(ast, "Num")):  # Python < 3.8
                return n.n
            elif isinstance(n, ast.BinOp):
                left = _eval(n.left)
                right = _eval(n.right)
                op_type = type(n.op)
                if op_type not in MATH_OPERATORS:
                    raise TypeError(f"Unsupported operator: {op_type.__name__}")
                return MATH_OPERATORS[op_type](left, right)
            elif isinstance(n, ast.UnaryOp):
                operand = _eval(n.operand)
                op_type = type(n.op)
                if op_type not in MATH_OPERATORS:
                    raise TypeError(f"Unsupported unary operator: {op_type.__name__}")
                return MATH_OPERATORS[op_type](operand)
            else:
                raise TypeError(f"Unsupported AST node type: {type(n).__name__}")
                
        result = _eval(node)
        return str(result)
    except Exception as e:
        logger.error(f"Safe calculator evaluation failed for expression '{expr}': {e}")
        return f"Error: Failed to evaluate expression. Reason: {str(e)}"


# --- TOOL MIDDLEWARE ---

def tool_middleware(func: Callable) -> Callable:
    """
    Middleware decorator that intercepts tool calls to:
    - Log execution details (name, timestamp, execution order, execution time, parameters, session_id).
    - Store the tool call metadata in PostgreSQL.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 1. Capture execution metadata
        start_time = time.time()
        timestamp = datetime.now(timezone.utc)
        
        # 2. Retrieve session_id from LangGraph RunnableConfig
        config = kwargs.get("config")
        session_id = None
        if config:
            configurable = getattr(config, "configurable", {}) if not isinstance(config, dict) else config.get("configurable", {})
            session_id = configurable.get("session_id")
        
        # 3. Resolve parameters (excluding system-injected config parameter)
        import inspect
        sig = inspect.signature(func)
        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        params = {k: v for k, v in bound.arguments.items() if k != "config"}
        
        # 4. Invoke tool logic
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error executing tool '{func.__name__}': {e}", exc_info=True)
            raise e
        finally:
            execution_time = time.time() - start_time
            
            # Log metrics as required
            logger.info(
                f"[Tool Middleware] Tool: {func.__name__} | "
                f"Session ID: {session_id} | "
                f"Params: {params} | "
                f"Timestamp: {timestamp.isoformat()} | "
                f"Execution Time: {execution_time:.6f}s"
            )
            
            # Store tool call records in database if session_id is active
            if session_id:
                # Parse to UUID format
                session_uuid = None
                if isinstance(session_id, str):
                    try:
                        session_uuid = uuid.UUID(session_id)
                    except ValueError:
                        logger.error(f"[Tool Middleware] Failed to parse session_id string '{session_id}' to UUID.")
                elif isinstance(session_id, uuid.UUID):
                    session_uuid = session_id
                
                if session_uuid:
                    db = SessionLocal()
                    try:
                        # Determine execution order
                        count = db.query(ToolCall).filter(ToolCall.session_id == session_uuid).count()
                        execution_order = count + 1
                        
                        tool_call_record = ToolCall(
                            session_id=session_uuid,
                            tool_name=func.__name__,
                            tool_arguments=params,
                            execution_order=execution_order,
                            execution_time=execution_time,
                            timestamp=timestamp
                        )
                        db.add(tool_call_record)
                        db.commit()
                        logger.info(
                            f"[Tool Middleware] Recorded tool call in database. "
                            f"Tool: {func.__name__}, Order: {execution_order}, Session: {session_uuid}"
                        )
                    except Exception as db_err:
                        db.rollback()
                        logger.error(f"[Tool Middleware] Failed to store tool call in database: {db_err}", exc_info=True)
                    finally:
                        db.close()
            else:
                logger.warning(
                    f"[Tool Middleware] No session_id found in config. "
                    f"Tool call details for '{func.__name__}' were logged but NOT saved to database."
                )
    return wrapper


# --- TOOLS DEFINITIONS ---

@tool
@tool_middleware
def search_documents(query: str, config: RunnableConfig) -> str:
    """
    Search the enterprise document repository for relevant info or document IDs matching a query.
    """
    query_lower = query.lower()
    results = []
    for doc_id, doc in MOCK_DOCUMENTS.items():
        if query_lower in doc["title"].lower() or query_lower in doc["content"].lower():
            results.append(f"- ID: {doc_id} | Title: {doc['title']}")
            
    if not results:
        return f"No enterprise documents found matching query: '{query}'"
    return "Matching documents found:\n" + "\n".join(results)


@tool
@tool_middleware
def read_document(doc_id: str, config: RunnableConfig) -> str:
    """
    Retrieve and read the full content of a specific enterprise document by its unique ID.
    """
    doc = MOCK_DOCUMENTS.get(doc_id)
    if not doc:
        return f"Error: Document with ID '{doc_id}' not found."
    return f"Document ID: {doc_id}\nTitle: {doc['title']}\nContent: {doc['content']}"


@tool
@tool_middleware
def calculator(expression: str, config: RunnableConfig) -> str:
    """
    Evaluate a mathematical expression safely. Supports standard arithmetic: +, -, *, /, **.
    """
    return eval_expr(expression)


@tool
@tool_middleware
def send_email(to_address: str, subject: str, body: str, config: RunnableConfig) -> str:
    """
    Send an email notification to a recipient customer or colleague (mock execution).
    """
    logger.info(f"[Mock Email] Sending to: {to_address} | Subject: {subject} | Body Length: {len(body)} chars")
    return f"Email successfully sent to {to_address} with subject '{subject}'."


@tool
@tool_middleware
def lookup_customer(customer_id: str, config: RunnableConfig) -> str:
    """
    Lookup customer record profile metrics including tier, email, status by customer ID.
    """
    cust = MOCK_CUSTOMERS.get(customer_id)
    if not cust:
        return f"Error: Customer record for ID '{customer_id}' not found."
    return (
        f"Customer Record:\n"
        f"- ID: {customer_id}\n"
        f"- Name: {cust['name']}\n"
        f"- Email: {cust['email']}\n"
        f"- Tier: {cust['tier']}\n"
        f"- Status: {cust['status']}"
    )
