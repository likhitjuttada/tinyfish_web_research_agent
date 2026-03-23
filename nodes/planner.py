import json
import os
from typing import List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from models.schemas import AgentState, TaskSpec, TaskSpecList

load_dotenv()

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "google")
    model_name = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    if provider == "openai":
        model = ChatOpenAI(model=model_name, api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
    elif provider == "anthropic":
        model = ChatAnthropic(model=model_name, api_key=os.getenv("ANTHROPIC_API_KEY"), temperature=0)
    elif provider == "google":
        model = ChatGoogleGenerativeAI(model=model_name, api_key=os.getenv("GOOGLE_API_KEY"), temperature=0)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

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