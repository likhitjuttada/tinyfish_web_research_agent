# Agent Instructions

## Overview

This is the TinyFish Research Agent — a Claude Code plugin that performs deep web research using TinyFish AI browser agents and synthesizes results with an LLM.

## Prerequisites

- Python 3.9+
- A `.env` file with `TINYFISH_API_KEY` and an LLM API key (see `.env.example`)
- `pip install -r requirements.txt` (or a virtual environment with dependencies installed)

## How This Plugin Works

1. The `/tinyfish:research` slash command runs `scripts/setup-research.sh` to validate deps and create a workspace.
2. The Stop hook (`hooks/orchestrator-stop-hook.sh`) automatically fires and runs the Python research pipeline.
3. Results are saved to `research/<research_id>/` and the hook returns a synthesis prompt.

## Testing

After making changes, verify the plugin structure:

```bash
# Check all required files exist
bash scripts/verify-plugin.sh
```

To run a manual test:

```bash
# Direct Python pipeline test (bypasses plugin system)
python main.py "What is RLHF?"
```

To test as a plugin:

```bash
# Load plugin locally in Claude Code
claude --plugin-dir /path/to/research_agent
# Then use:
/tinyfish:research "What is RLHF?"
```
