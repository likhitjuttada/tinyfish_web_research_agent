import asyncio
import aiohttp
import time
from typing import List, Dict, Any
from models.schemas import TaskSpecList
from models.schemas import AgentState, TaskSpec, BrowserResult
from config import TINYFISH_API_KEY, TINYFISH_API_BASE_URL

async def run_tinyfish(session: aiohttp.ClientSession, url: str, goal: str) -> str:
    """Submits a single run to TinyFish and returns the run ID."""
    async with session.post(
        f"{TINYFISH_API_BASE_URL}/automation/run-async",
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
        return result.get("run_id")

async def get_run_result(session: aiohttp.ClientSession, run_id: str) -> Dict[str, Any]:
    """Polls a run status until completion and returns the final data."""
    while True:
        async with session.get(
            f"{TINYFISH_API_BASE_URL}/runs/{run_id}",
            headers={"Authorization": f"Bearer {TINYFISH_API_KEY}"}
        ) as response:
            response.raise_for_status()
            data = await response.json()
            
            status = data.get("status")
            if status == "completed":
                return data
            elif status == "failed":
                raise Exception(f"Run {run_id} failed: {data.get('error')}")
            
            # Wait before polling again
            await asyncio.sleep(5)

async def synthesizer(data):
    with open(f"output/{slug}.md", "w") as f:
        f.write(data)
    return 0

async def browser_executor(task_list: TaskSpecList) -> AgentState:
    """
    Browser executor node.
    Submits tasks as "fire and forget" runs, then polls for completion.
    """
    print(f"--- SUBMITTING {len(task_list.tasks)} RESEARCH TASKS ---")
    
    start_time = time.time()
    print(task_list.tasks)
    
    async with aiohttp.ClientSession() as session:
        # Submit all tasks
        submit_tasks = [
            run_tinyfish(session, task.url, task.goal)
            for task in task_list.tasks
        ]
        run_ids = await asyncio.gather(*submit_tasks)
        print(run_ids)
        
        
        # # 2. Poll for all results
        # print("Polling for results...")
        # poll_tasks = [get_run_result(session, rid) for rid in run_ids]
        
        # # Using return_exceptions=True to handle individual failures gracefully
        # finished_results = await asyncio.gather(*poll_tasks, return_exceptions=True)
        
        # browser_results = []
        # for idx, res in enumerate(finished_results):
        #     if isinstance(res, Exception):
        #         print(f"Task {run_ids[idx]} failed: {res}")
        #         continue
            
    #         browser_results.append(BrowserResult(
    #             source_url=res.get("url", ""),
    #             platform=state["task_specs"][idx].platform_url,
    #             raw_content=res.get("content", ""),
    #             extracted_snippets=res.get("snippets", []),
    #             metadata=res.get("metadata", {})
    #         ))
    
    # elapsed_time = time.time() - start_time
    
    # metadata = state.get("metadata", {})
    # metadata["session_count"] = len(browser_results)
    # metadata["time_elapsed"] = elapsed_time
    # metadata["run_ids"] = run_ids
    
    # return {
    #     "raw_results": browser_results,
    #     "run_ids": run_ids,
    #     "metadata": metadata
    # }
