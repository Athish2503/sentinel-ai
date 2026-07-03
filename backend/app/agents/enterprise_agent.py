from typing import Annotated, Sequence, TypedDict, Dict, Any, List
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END, add_messages
from langgraph.prebuilt import ToolNode

from app.llm import LLMFactory
from app.utils.config import settings
from app.utils.logger import logger
from app.tools.agent_tools import (
    search_documents,
    read_document,
    calculator,
    send_email,
    lookup_customer
)

# Define the State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Retrieve/Initialize LLM Model
def get_agent_llm() -> ChatGroq:
    """
    Instantiates the Groq Chat model using credentials from configurations via LLMFactory.
    """
    logger.info("Initializing Groq LLM using LLMFactory.")
    return LLMFactory.create().get_client()

# List of enterprise assistant tools
enterprise_tools = [
    search_documents,
    read_document,
    calculator,
    send_email,
    lookup_customer
]

# Set up the Tool Execution Node
tool_node = ToolNode(enterprise_tools)

# Define the Agent Model Invocation Node
def call_model(state: AgentState, config: RunnableConfig):
    """
    Calls the Groq LLM with bound tools and current conversation state.
    """
    llm = get_agent_llm()
    # Bind the tools suite to the Groq model
    llm_with_tools = llm.bind_tools(enterprise_tools)
    
    messages = state["messages"]
    
    # System Instructions for the Enterprise Assistant
    system_prompt = (
        "You are a helpful and precise enterprise assistant. "
        "You have access to search_documents, read_document, calculator, "
        "send_email, and lookup_customer. Use them to answer user questions.\n"
        "Guidance:\n"
        "- If you need to search, first use search_documents. Then read the document content "
        "using read_document using its ID.\n"
        "- If calculations are required, use the calculator tool. Do not guess.\n"
        "- Provide a professional, concise, and complete summary when answering. "
        "Do not output technical JSON strings or dictionary structures in the final response "
        "unless explicitly asked; format customer records and document summaries clearly for humans."
    )
    
    # Prepend system instruction if not already present
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=system_prompt)] + list(messages)
    
    response = llm_with_tools.invoke(messages, config=config)
    return {"messages": [response]}

# Define routing conditional logic
def should_continue(state: AgentState):
    """
    Determines whether the LLM wants to run tools (action) or finish (end).
    """
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "action"
    return "end"

# Set up the ReAct Agent Graph
workflow = StateGraph(AgentState)

# Add Agent and Tool nodes
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set starting point
workflow.set_entry_point("agent")

# Add conditional path from agent to tools/end
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "action": "action",
        "end": END
    }
)

# Connect tool executions back to the agent for next decision
workflow.add_edge("action", "agent")

# Compile the graph
agent_graph = workflow.compile()
