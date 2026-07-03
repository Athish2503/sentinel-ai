# Kavalar: System Architecture Detail

This document outlines the detailed system architecture, modules, database schema, and data flows within Kavalar.

---

## 🗺️ Architectural Diagram

The system coordinates the agent run, database interceptor logging, and anomaly evaluation in an asynchronous FastAPI structure.

```mermaid
flowchart TD
    %% Define Subgraphs
    subgraph Frontend [Next.js Dashboard UI]
        Dashboard[Governance Dashboard]
        ThreatConsole[Threat Console Simulator]
        FlowGraph[Interactive Flow Visualizer]
    end

    subgraph BackendAPI [FastAPI Gateway]
        AgentRouter[POST /api/v1/agent/run]
        BaselineRouter[POST /api/v1/baseline/train]
        SimulateRouter[POST /api/v1/simulate/{id}]
    end

    subgraph LangGraphSystem [LangGraph Engine]
        AgentState[AgentState dict]
        ModelNode[Agent Model Node]
        ToolNode[Action Tool Node]
        Middleware[Tool Interceptor Middleware]
    end

    subgraph Database [PostgreSQL / SQLite]
        SessionDB[(Session Table)]
        ToolCallDB[(Tool Call Logs Table)]
        BaselineDB[(Baseline Profile Table)]
        AlertDB[(Anomaly Alerts Table)]
    end

    subgraph DetectionEngine [ML / Rule Engine]
        Features[Feature Extractor]
        IForest[Isolation Forest Model]
        Explainer[Behavior Explainer Rules]
    end

    %% Communication Connections
    Dashboard -->|API Calls| BackendAPI
    ThreatConsole -->|POST /simulate| SimulateRouter
    
    AgentRouter -->|Spawns Graph| ModelNode
    SimulateRouter -->|Patches & Spawns Graph| ModelNode
    
    ModelNode -->|Conditional Route| ToolNode
    ToolNode -->|Wraps execution| Middleware
    Middleware -->|Intercepts & logs| ToolCallDB
    Middleware -->|Execution output| ModelNode
    
    %% Detection Evaluation
    SimulateRouter -->|Triggers prediction| Features
    Features -->|Reads| ToolCallDB
    Features -->|Builds Behavior Vector| IForest
    IForest -->|Decision Score| Explainer
    Explainer -->|Saves Score & Reason| SessionDB
    Explainer -->|If Anomaly| AlertDB
    
    %% UI Population
    SessionDB -.->|Polls sessions| Dashboard
    AlertDB -.->|Polls alerts| Dashboard
    ToolCallDB -.->|Builds sequence graph| FlowGraph
```

---

## 🤖 LangGraph ReAct Assistant Agent

The agent is implemented as a compiled state graph (`StateGraph`) that executes a **Reasoning and Acting (ReAct)** loop.

### 1. State Definition
The graph coordinates state via a `TypedDict` containing the message history:
```python
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
```

### 2. Node Flow & Routing
*   **Agent Model Node (`agent`)**: Constructs a system message instructing the LLM, binds the suite of five enterprise tools (`search_documents`, `read_document`, `calculator`, `send_email`, `lookup_customer`), and queries the model.
*   **Conditional Routing (`should_continue`)**: Inspects the last message returned by the model:
    *   If the model wants to call tools (`last_message.tool_calls` is not empty), it routes the flow to the `action` node.
    *   If no tool calls are requested, it ends execution (`END`).
*   **Action Tool Node (`action`)**: Executes the requested tools via LangGraph's `ToolNode` and appends the resulting `ToolMessage`s to the state, routing back to the `agent` node.

---

## ⚡ Tool Execution Interceptor Middleware

All tools are wrapped in the `@tool_middleware` decorator in `backend/app/tools/agent_tools.py`. This acts as an auditing sidecar:

1.  **Latency Tracking**: Starts a timer prior to executing the tool and captures total elapsed execution time (`execution_time = time.time() - start_time`).
2.  **Context Resolution**: Reads the LangGraph `RunnableConfig` parameters to resolve the active `session_id`.
3.  **Argument Inspection**: Captures the exact parameters provided to the tool.
4.  **Database Recording**: Opens a thread-safe connection to the SQL engine and inserts a new `ToolCall` record containing the tool name, sequence index (determined by counting existing calls in the session), payload size, timestamp, and duration.

---

## 💾 Database Schema (SQLAlchemy ORM)

The database (SQLite for local sandbox testing, PostgreSQL for Supabase integration) consists of five main tables:

### 1. `sessions` Table
Stores overall session metadata and anomaly score evaluations.
*   `id`: `UUID` (Primary Key)
*   `prompt`: `Text` (The initial prompt sent by the user)
*   `status`: `String` (e.g., `pending`, `completed`, `failed`, `Injected`, `Normal`)
*   `anomaly_score`: `Float` (Computed probability of prompt injection, scaled `0.0 - 1.0`)
*   `created_at`: `DateTime`

### 2. `tool_calls` Table
Logs individual tool invocations by the agent state graph.
*   `id`: `Integer` (Primary Key)
*   `session_id`: `UUID` (Foreign Key -> `sessions.id`)
*   `tool_name`: `String` (Name of the tool, e.g., `send_email`)
*   `tool_arguments`: `JSON` (Stringified arguments dictionary)
*   `execution_order`: `Integer` (Sequence index, e.g., `1`, `2`)
*   `execution_time`: `Float` (Duration in seconds)
*   `timestamp`: `DateTime`

### 3. `baselines` Table
Tracks versioned training baselines of normal behavior profiles.
*   `id`: `UUID` (Primary Key)
*   `model_version`: `String` (Timestamped version code, e.g., `v20260703110536`)
*   `training_runs`: `Integer` (Number of standard sessions profiled, e.g., `25`)
*   `threshold`: `Float` (Isolation Forest contamination decision boundary threshold)
*   `created_at`: `DateTime`

### 4. `baseline_feature_vectors` Table
Saves the specific features extracted from the baseline training runs.
*   `id`: `Integer` (Primary Key)
*   `baseline_id`: `UUID` (Foreign Key -> `baselines.id`)
*   `session_id`: `UUID` (The profiled training run session ID)
*   `prompt`: `Text`
*   `sequence`: `JSON` (List of tools executed in order)
*   `tool_frequency`: `JSON` (Map of tool names to frequencies)
*   `execution_order`: `JSON` (List of ordered tool names)
*   `execution_count`: `Integer` (Total tool calls)
*   `average_execution_time`: `Float`
*   `parameter_length`: `Integer` (Sum of character lengths of arguments)

### 5. `alerts` Table
Records flagged prompt injection attempts.
*   `id`: `Integer` (Primary Key)
*   `session_id`: `UUID` (Foreign Key -> `sessions.id`)
*   `score`: `Float` (Scale `0.0 - 1.0`)
*   `reason`: `Text` (Bullet-point checklist explanation of the anomalous behaviors)
*   `status`: `String` (Default `Active`, can be resolved/suppressed)
*   `created_at`: `DateTime`

---

## 🔌 API Gateway Endpoints

The API is fully documented under `/api/v1` and structures the governance workflows:

| Route | Method | Description |
|---|---|---|
| `/api/v1/agent/run` | `POST` | Run the live LangGraph agent with custom user prompts. |
| `/api/v1/baseline/train` | `POST` | Start a baseline training run (triggers 20-30 normal simulations). |
| `/api/v1/baseline/active` | `GET` | Retrieve the active baseline training statistics and vocabulary. |
| `/api/v1/detect` | `POST` | Trigger manual feature extraction and Isolation Forest prediction for a session. |
| `/api/v1/simulate/{id}` | `POST` | Execute sandbox attack simulation scenarios `0`, `1`, `2`, or `3`. |
| `/api/v1/sessions` | `GET` | List all historical agent sessions and their anomaly levels. |
| `/api/v1/alerts` | `GET` | List all flagged threat alerts. |
