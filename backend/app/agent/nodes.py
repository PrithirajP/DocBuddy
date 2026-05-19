from langchain_core.messages import SystemMessage
from app.utils.hf_client import get_hf_llm
from app.agent.tools import evaluator_tools
from langgraph.graph import END

llm = get_hf_llm()
model_with_tools = llm.bind_tools(evaluator_tools)

async def clinical_evaluator_node(state: dict):
    messages = state["messages"]
    
    if not any(isinstance(m, SystemMessage) for m in messages):
        sys_msg = SystemMessage(
            content=(
                "You are DocBuddy, a highly advanced, empathetic clinical diagnostic orchestrator. "
                "You are the primary conversational interface for patients. You have a team of specialized AI tools at your disposal.\n\n"
                "ROUTING RULES:\n"
                "- If the user describes symptoms, you MUST use the 'analyze_symptoms_for_disease' tool to consult the Medical Specialist AI.\n"
                "- If the user asks about diets or nutrition, you MUST use the 'generate_diet_plan' tool to consult the Dietitian AI.\n"
                "- If the user mentions medications, you MUST use the 'analyze_medications' tool to check the FDA/NIH databases.\n"
                "- If the user needs a physical doctor or clinic, you MUST use the 'search_doctors' tool to check the global map database.\n\n"
                "When your tools return information, summarize their findings warmly and clearly for the patient using markdown bullet points. "
                "CRITICAL: Always include a brief disclaimer that you are an AI assistant and they should consult a real doctor for medical emergencies."
            )
        )
        messages = [sys_msg] + messages
        
    response = await model_with_tools.ainvoke(messages)
    
    return {"messages": [response]}

def should_continue(state: dict) -> str:
    """Determines if the agent wants to use a tool or reply to the user."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END