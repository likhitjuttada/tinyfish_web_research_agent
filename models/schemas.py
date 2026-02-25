from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from pydantic import HttpUrl

class TaskSpec(BaseModel):
    """Specification for a single research task."""
    url: str = Field(description="The full and valid URL to search (e.g., https://www.youtube.com, https://x.com, https://github.com, https://reddit.com)")
    goal: str = Field(description="What specific information should be extracted from this source")

class TaskSpecList(BaseModel):
    """List of task specifications."""
    tasks: List[TaskSpec]

class BrowserResult(BaseModel):
    """Result from a TinyFish browser session."""
    url: str
    goal: str
    raw_content: Dict[str, Any]
    # extracted_snippets: List[str]
    metadata: Dict[str, Any]

class AgentState(TypedDict):
    """The state of the research agent."""
    query: str
    task_specs: List[TaskSpec]
    run_ids: List[str]  # All submitted run IDs
    pending_run_ids: List[str]  # Run IDs still being polled
    raw_results: List[BrowserResult]
    final_document: str
    metadata: Dict[str, Any]
    polling_attempt: int  # Current index in backoff schedule
