from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import retrieve_node, plan_node, generate_node, validate_node

# definition
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("plan", plan_node)
workflow.add_node("generate", generate_node)
workflow.add_node("validate", validate_node)

from typing import Literal

# ...

# Conditional Logic
def route_after_plan(state: AgentState) -> Literal["generate", END]:
    plan = state["plan"]
    if "STATUS: INCOMPLETE" in plan:
        return END
    return "generate"

def route_after_validate(state: AgentState) -> Literal["generate", END]:
    feedback = state.get("feedback", "PASS")
    attempts = state.get("attempt_count", 0)
    
    # If passed or retried too many times, stop
    if feedback == "PASS" or attempts >= 3:
        if attempts >= 3:
            print("⚠️ Max retries reached. Returning best effort.")
        return END
        
    return "generate"

# Add Edges
# START -> Retrieve -> Plan -> (Decision) -> Generate -> Validate -> (Loop or End)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "plan")
workflow.add_conditional_edges("plan", route_after_plan)
workflow.add_edge("generate", "validate")
workflow.add_conditional_edges("validate", route_after_validate)

# Compile
app_graph = workflow.compile()
