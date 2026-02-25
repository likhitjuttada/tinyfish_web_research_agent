from langgraph.graph import StateGraph, END
from models.schemas import AgentState
from nodes.planner import query_planner
from nodes.executor import browser_executor
from nodes.synthesizer import synthesizer

def create_research_graph():
    """
    Creates and compiles the LangGraph StateGraph.
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", query_planner)
    workflow.add_node("executor", browser_executor)
    workflow.add_node("synthesizer", synthesizer)

    # Define edges
    # Standard linear flow: planner -> executor -> synthesizer -> END
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "synthesizer")
    workflow.add_edge("synthesizer", END)

    # Compile the graph
    return workflow.compile()
