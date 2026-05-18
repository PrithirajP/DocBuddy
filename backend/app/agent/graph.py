from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from app.agent.state import PatientState
from app.agent.nodes import clinical_evaluator_node, should_continue
from app.agent.tools import evaluator_tools

# 1. Initialize the graph with our state schema
workflow = StateGraph(PatientState)

# 2. Define the prebuilt ToolNode
# This node automatically executes the Python functions requested by the LLM
tool_node = ToolNode(evaluator_tools)

# 3. Add the nodes to the graph
workflow.add_node("agent", clinical_evaluator_node)
workflow.add_node("tools", tool_node)

# 4. Define the execution flow (Edges)
# Start -> Agent
workflow.add_edge(START, "agent")

# Agent -> decides -> Tools OR End
workflow.add_conditional_edges(
    "agent", 
    should_continue, 
    ["tools", END]
)

# Tools -> goes back to -> Agent (so the agent can read the tool's output and summarize)
workflow.add_edge("tools", "agent")

# 5. Compile the graph into an executable application
health_evaluator = workflow.compile()