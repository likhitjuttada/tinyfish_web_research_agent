import asyncio
import aiohttp
import json
import os
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
from models.schemas import TaskSpecList
from models.schemas import AgentState, TaskSpec, BrowserResult
from config import TINYFISH_API_KEY, TINYFISH_API_BASE_URL

# Load environment variables
load_dotenv()

# Directory for saving raw per-source results
INTERMEDIATE_DIR = os.path.join(os.path.dirname(__file__), "..", "intermediate_results")
os.makedirs(INTERMEDIATE_DIR, exist_ok=True)


def _save_intermediate_result(run_id: str, response: dict) -> str:
    """Persist a single run's raw API response to disk as JSON."""
    filepath = os.path.join(INTERMEDIATE_DIR, f"{run_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(response, f, indent=2, default=str)
    print(f"Saved intermediate result: {filepath}")
    return filepath


async def submit_tinyfish_run(session, url, goal):
    """Submit a tinyfish run and return the run_id"""
    async with session.post(
        "https://agent.tinyfish.ai/v1/automation/run-async",
        headers={
            "X-API-Key": TINYFISH_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "url": url,
            "goal": goal,
        },
    ) as response:
        result = await response.json()
        return result["run_id"]

async def get_run_status(session, run_id):
    """Get the status of a specific run"""
    async with session.get(
        f"https://agent.tinyfish.ai/v1/runs/{run_id}",
        headers={
            "X-API-Key": TINYFISH_API_KEY,
        },
    ) as response:
        return await response.json()

async def wait_for_completion(session, run_id, poll_interval=5):
    """Poll a run until it completes"""
    while True:
        response = await get_run_status(session, run_id)
        status = response.get("status")

        if status in ["COMPLETED", "FAILED", "CANCELLED"]:
            return response

        await asyncio.sleep(poll_interval)

async def browser_submitter(tasklist: TaskSpecList) -> Dict[str, Any]:
    """Submit research tasks to TinyFish and store run_ids in state."""
    task_specs = tasklist.tasks
    if not task_specs:
        return {"run_ids": [], "pending_run_ids": [], "polling_attempt": 0}

    print(f"--- SUBMITTING {len(task_specs)} RESEARCH TASKS ---")
    
    async with aiohttp.ClientSession() as session:
        submit_tasks = [
            submit_tinyfish_run(session, task.url, task.goal)
            for task in task_specs
        ]
        run_ids = await asyncio.gather(*submit_tasks)
        print(f"Submitted {len(run_ids)} runs: {run_ids}")

    return {
        "run_ids": run_ids, 
        "pending_run_ids": run_ids,
        "polling_attempt": 0,
        "raw_results": []
    }

async def browser_poller(state: AgentState) -> Dict[str, Any]:
    """Poll pending run IDs and update results."""
    pending_run_ids = state.get("pending_run_ids", [])
    if not pending_run_ids:
        return {}

    attempt = state.get("polling_attempt", 0)
    print(f"--- POLLING {len(pending_run_ids)} PENDING RUNS (Attempt {attempt}) ---")
    
    results = state.get("raw_results", [])
    still_pending = []
    
    async with aiohttp.ClientSession() as session:
        # Check status of all pending runs
        status_tasks = [get_run_status(session, rid) for rid in pending_run_ids]
        responses = await asyncio.gather(*status_tasks)
        
        for idx, res in enumerate(responses):
            run_id = pending_run_ids[idx]
            status = res.get("status")
            
            if status in ["COMPLETED", "FAILED", "CANCELLED"]:
                print(f"Run {run_id} finished with status: {status}")
                _save_intermediate_result(run_id, res)
                results.append(BrowserResult(
                    url=res.get("url", ""),
                    goal=res.get("goal", ""),
                    raw_content=res.get("result", ""),
                    # extracted_snippets=res.get("snippets", []),
                    metadata=res.get("metadata", {})
                ))
            else:
                still_pending.append(run_id)

    return {
        "pending_run_ids": still_pending,
        "raw_results": results,
        "polling_attempt": attempt + 1
    }
