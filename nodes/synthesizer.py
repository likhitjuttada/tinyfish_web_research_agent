import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from models.schemas import AgentState

load_dotenv()

def get_llm():
    provider = os.getenv("LLM_PROVIDER", "google")
    model_name = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    if provider == "openai":
        return ChatOpenAI(model=model_name, api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7)
    elif provider == "anthropic":
        return ChatAnthropic(model=model_name, api_key=os.getenv("ANTHROPIC_API_KEY"), temperature=0.7)
    elif provider == "google":
        return ChatGoogleGenerativeAI(model=model_name, api_key=os.getenv("GOOGLE_API_KEY"), temperature=0.7)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

async def synthesizer(state: AgentState) -> dict:
    """
    Synthesizer node.
    Takes all raw results and produces a unified, structured research document.
    """
    print("--- SYNTHESIZING RESEARCH RESULTS ---")
    
    # Format results for the prompt
    formatted_results = ""
    for idx, result in enumerate(state["raw_results"]):
        formatted_results += f"Source {idx+1}: {result.url}\n"
        formatted_results += f"Content: {result.raw_content}\n" # Truncate for prompt length
        # formatted_results += f"Snippets: {', '.join(result.extracted_snippets)}\n"
        formatted_results += "-" * 20 + "\n"
    
    # Load prompt
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "synthesizer_prompt.txt")
    with open(prompt_path, "r") as f:
        content = f.read()
        system_prompt = content.replace("{query}", state["query"]).replace("{results}", formatted_results)
    
    llm = get_llm()
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Synthesize the results for: {state['query']}")
    ]
    
    response = await llm.ainvoke(messages)
    
    return {
        "final_document": response.content
    }
