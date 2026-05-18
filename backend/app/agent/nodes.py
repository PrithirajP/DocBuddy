from langchain_core.messages import SystemMessage
from app.utils.hf_client import get_hf_llm
from app.agent.tools import evaluator_tools
from langgraph.graph import END

# 1. Initialize the model and bind the tools to it
llm = get_hf_llm()
model_with_tools = llm.bind_tools(evaluator_tools)

def clinical_evaluator_node(state: dict):
    """The main reasoning agent that talks to the patient and decides if tools are needed."""
    messages = state["messages"]
    
    # Inject a system persona if this is the start of the conversation
    if not any(isinstance(m, SystemMessage) for m in messages):
        sys_msg = SystemMessage(
            content=(
                "You are an empathetic, agentic AI Health Evaluator. "
                "Your goal is to analyze symptoms, check medication interactions, and recommend routines or doctors. "
                "You MUST clearly state that you are an AI, not a doctor, and your advice does not replace professional medical consultation. "
                "Use your tools whenever you need to check drug interactions, find a doctor, or generate a diet."
            )
        )
        messages = [sys_msg] + messages
        
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: dict) -> str:
    """Determines if the graph should execute a tool or stop and reply to the user."""
    last_message = state["messages"][-1]
    
    if last_message.tool_calls:
        return "tools"
    
    return END