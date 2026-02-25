from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

class TaskSpec(BaseModel):
    """Specification for a single research task."""
    url: str = Field(description="The URL to search (e.g., youtube.com, x.com, github.com, reddit.com)")
    goal: str = Field(description="What specific information should be extracted from this source")

class TaskSpecList(BaseModel):
    """List of task specifications."""
    tasks: List[TaskSpec]

class BrowserResult(BaseModel):
    """Result from a TinyFish browser session."""
    url: str
    goal: str
    raw_content: str
    extracted_snippets: List[str]
    metadata: Dict[str, Any]

class AgentState(TypedDict):
    """The state of the research agent."""
    query: str
    task_specs: List[TaskSpec]
    run_ids: List[str]
    raw_results: List[BrowserResult]
    final_document: str
    metadata: Dict[str, Any]
