import sys
import asyncio
import os
import re
from datetime import datetime
from graph import create_research_graph

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

async def main():
    args = sys.argv[1:]
    workspace = None

    # Parse --workspace <path>
    if "--workspace" in args:
        idx = args.index("--workspace")
        workspace = args[idx + 1]
        args = args[:idx] + args[idx + 2:]

    if not args:
        print("Usage: python main.py [--workspace <dir>] \"your research query here\"")
        sys.exit(1)

    query = args[0]

    # If no workspace given, create one under research/
    if workspace is None:
        slug = slugify(query)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        workspace = os.path.join("research", f"{slug}-{timestamp}")

    workspace = os.path.abspath(workspace)
    intermediate_dir = os.path.join(workspace, "intermediate")
    os.makedirs(intermediate_dir, exist_ok=True)

    # Expose workspace to executor via env var
    os.environ["RESEARCH_WORKSPACE"] = workspace

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
    print(f"Workspace: {workspace}")

    app = create_research_graph()
    final_output = await app.ainvoke(initial_state, config={"recursion_limit": 100})

    # Save the final report directly into the workspace
    report_path = os.path.join(workspace, "final-report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(final_output["final_document"])

    sources_count = len(final_output.get("raw_results", []))

    print("\n" + "="*50)
    print("RESEARCH COMPLETE")
    print(f"Report: {report_path}")
    print(f"Sources searched: {sources_count}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
