from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from app.agent.state import PatientState
from app.agent.nodes import clinical_evaluator_node, should_continue
from app.agent.tools import evaluator_tools

workflow = StateGraph(PatientState)
tool_node = ToolNode(evaluator_tools)

workflow.add_node("agent", clinical_evaluator_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

# Initialize the short-term RAM checkpointer
memory = MemorySaver()

# Compile the graph and attach the memory
health_evaluator = workflow.compile(checkpointer=memory)