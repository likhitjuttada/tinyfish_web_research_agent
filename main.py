import sys
import asyncio
import os
import re
from datetime import datetime
from graph import create_research_graph
from config import OUTPUT_DIR

def slugify(text):
    """
    Simple slugify for filenames.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

async def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py \"your research query here\"")
        sys.exit(1)
    
    query = sys.argv[1]
    
    # Initialize state
    initial_state = {
        "query": query,
        "task_specs": [],
        "raw_results": [],
        "final_document": "",
        "metadata": {
            "start_time": datetime.now().isoformat()
        }
    }
    
    print(f"Starting research for: '{query}'")
    
    # Create the graph
    app = create_research_graph()
    
    # Run the graph
    # Using 'final_state' to access the results after execution
    final_output = await app.ainvoke(initial_state)
    
    # Save the output
    slug = slugify(query)
    filename = f"{slug}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(final_output["final_document"])
    
    # Print summary
    metadata = final_output.get("metadata", {})
    sources_count = len(final_output.get("raw_results", []))
    time_elapsed = metadata.get("time_elapsed", 0)
    
    print("\n" + "="*50)
    print("RESEARCH COMPLETE")
    print(f"Document saved to: {filepath}")
    print(f"Sources searched: {sources_count}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
