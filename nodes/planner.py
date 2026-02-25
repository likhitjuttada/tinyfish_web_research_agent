import json
import os
from typing import List
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from models.schemas import AgentState, TaskSpec, TaskSpecList
from config import LLM_PROVIDER, LLM_MODEL, OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY 

def get_llm():
    if LLM_PROVIDER == "openai":
        model= ChatOpenAI(model=LLM_MODEL, api_key=OPENAI_API_KEY, temperature=0)
    elif LLM_PROVIDER == "anthropic":
        model= ChatAnthropic(model=LLM_MODEL, api_key=ANTHROPIC_API_KEY, temperature=0)
    elif LLM_PROVIDER == "google":
        model= ChatGoogleGenerativeAI(model=LLM_MODEL, api_key=GOOGLE_API_KEY, temperature=0)
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")
    
    return model.with_structured_output(TaskSpecList)

async def query_planner(state: AgentState) -> TaskSpecList:
    """
    Query planner node.
    Decomposes the user query into a list of specific research tasks.
    """
    print(f"--- PLANNING RESEARCH FOR: {state['query']} ---")
    
    # Load prompt
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "planner_prompt.txt")
    with open(prompt_path, "r") as f:
        system_prompt = f.read().replace("{query}", state["query"])
    
    llm = get_llm()
    
    # We use structured output if possible, but for boilerplate we can also just parse JSON
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Plan research for: {state['query']}")
    ]
    
    response = await llm.ainvoke(messages)
    
    return response