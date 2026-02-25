import asyncio
from typing import Literal
from langgraph.graph import StateGraph, END
from models.schemas import AgentState
from nodes.planner import query_planner
from nodes.executor import browser_submitter, browser_poller
from nodes.synthesizer import synthesizer

POLLING_INTERVALS = [2, 2, 4, 4, 4, 6, 6, 7, 8, 8]

async def wait_node(state: AgentState) -> AgentState:
    """Sleep for the duration of the current polling interval."""
    attempt = state.get("polling_attempt", 0)
    # Clamp attempt index to list length - 1, then use last value for any subsequent attempts
    interval_idx = min(attempt, len(POLLING_INTERVALS) - 1)
    sleep_time = POLLING_INTERVALS[interval_idx]
    
    print(f"--- WAITING {sleep_time}s FOR NEXT POLL ---")
    await asyncio.sleep(sleep_time)
    return state

def polling_router(state: AgentState) -> Literal["wait_node", "synthesizer"]:
    """Route to wait_node if there are pending runs, else synthesizer."""
    if state.get("pending_run_ids"):
        return "wait_node"
    return "synthesizer"

def create_research_graph():
    """
    Creates and compiles the LangGraph StateGraph.
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", query_planner)
    workflow.add_node("submitter", browser_submitter)
    workflow.add_node("poller", browser_poller)
    workflow.add_node("wait_node", wait_node)
    workflow.add_node("synthesizer", synthesizer)

    # Define edges
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "submitter")
    workflow.add_edge("submitter", "poller")
    
    # Check if we need to poll again or move to synthesizer
    workflow.add_conditional_edges(
        "poller",
        polling_router,
        {
            "wait_node": "wait_node",
            "synthesizer": "synthesizer"
        }
    )
    
    # Loop back from wait_node to poller
    workflow.add_edge("wait_node", "poller")
    workflow.add_edge("synthesizer", END)

    # Compile the graph
    return workflow.compile()
