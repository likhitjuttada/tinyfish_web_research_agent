# TinyFish Research Agent

A powerful, autonomous research agent built with **LangGraph** and **TinyFish AI**. This agent takes a research query, plans a series of targeted web searches, executes them using TinyFish's headless browser automation, and synthesizes the findings into a comprehensive research document.

**Available as a [Claude Code Plugin](#-claude-code-plugin) or a [standalone CLI](#-standalone-cli-usage).**

## 🚀 Features

- **Autonomous Planning**: Decomposes complex research queries into actionable tasks with specific URLs and goals.
- **Headless Browser Execution**: Uses [TinyFish AI](https://tinyfish.ai) to interact with websites and extract content.
- **State-Managed Polling**: Implements a robust polling mechanism with custom backoff intervals (`[2, 2, 4, 4, 4, 6, 6, 7, 8, 8]`) to efficiently wait for browser tasks to complete.
- **Multi-LLM Support**: Supports OpenAI, Anthropic, and Google Gemini via LangChain.
- **Structured Synthesis**: Aggregates results from multiple sources into a unified Markdown report.
- **Intermediate Results**: Saves raw per-source results as JSON for debugging and transparency.

## 🏗️ Architecture

The agent is built using a directed acyclic graph (DAG) via LangGraph:

1.  **Planner**: Generates research tasks from the query.
2.  **Submitter**: Submits tasks to TinyFish as asynchronous "fire-and-forget" runs.
3.  **Poller**: Periodic checks for completed runs.
4.  **Wait Node**: Implements the polling delay with backoff logic.
5.  **Synthesizer**: Finalizes the research document once all data is collected.

---

## 🔌 Claude Code Plugin

### Installation

**From within Claude Code:**
```
/plugin marketplace add likhitjuttada/tinyfish_web_research_agent
/plugin install tinyfish-research@likhitjuttada-claude-marketplace
```

**From the command line:**
```bash
claude plugin marketplace add likhitjuttada/tinyfish_web_research_agent
claude plugin install tinyfish-research@likhitjuttada-claude-marketplace
```

**Manual installation (for development):**
```bash
git clone https://github.com/likhitjuttada/tinyfish_web_research_agent.git
cd tinyfish_web_research_agent
pip install -r requirements.txt
# Configure .env (see below), then in Claude Code:
claude --plugin-dir /path/to/tinyfish_web_research_agent
```

### Plugin Usage

```
/tinyfish:research How does RLHF work?
```

The plugin will:
1. Validate prerequisites and create a research workspace
2. Submit browser tasks to TinyFish AI
3. Poll for results with increasing backoff intervals
4. Synthesize findings and present them directly in Claude Code

**Cancel an active session:**
```
/tinyfish:cancel-research
```

**Monitor progress:**
```bash
tail -f research/<research_id>/progress.log
```

### Plugin Architecture

```
User → /tinyfish:research → setup-research.sh (validates + creates state)
                                    ↓
                          Claude finishes response
                                    ↓
                          Stop Hook fires automatically
                                    ↓
                          run-research.sh → python main.py
                                    ↓
                          Results saved → Hook returns synthesis prompt
                                    ↓
                          Claude reads results and presents summary
```

---

## 🖥️ Standalone CLI Usage

### Prerequisites
- Python 3.9+
- A TinyFish API Key
- An LLM API Key (OpenAI, Anthropic, or Google)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/likhitjuttada/tinyfish_web_research_agent.git
   cd tinyfish_web_research_agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables — create a `.env` file:
   ```env
   TINYFISH_API_KEY=your_tinyfish_key
   LLM_PROVIDER=google  # or openai, anthropic
   GOOGLE_API_KEY=your_google_key
   LLM_MODEL=gpt-4-turbo  # optional, if using openai
   ```

### CLI Usage

```bash
python main.py "Your research topic here"
```

The final document will be saved in the `output/` directory as a Markdown file.

---

## 📁 Project Structure

```
├── .claude-plugin/          # Plugin manifest files
│   ├── plugin.json          # Plugin metadata
│   └── marketplace.json     # Marketplace listing
├── commands/                # Slash commands
│   ├── research.md          # /tinyfish:research
│   └── cancel-research.md   # /tinyfish:cancel-research
├── hooks/                   # Lifecycle hooks
│   ├── hooks.json           # Hook registration
│   └── orchestrator-stop-hook.sh
├── scripts/                 # Shell scripts
│   ├── setup-research.sh    # Validation + workspace setup
│   └── run-research.sh      # Runs the Python pipeline
├── nodes/                   # Python pipeline nodes
│   ├── executor.py          # TinyFish submission + polling
│   ├── planner.py           # LLM query planning
│   └── synthesizer.py       # Result synthesis
├── models/                  # Pydantic schemas
├── prompts/                 # LLM prompt templates
├── main.py                  # CLI entry point
├── graph.py                 # LangGraph workflow
├── config.py                # Configuration
├── AGENTS.md                # Agent instructions
├── CLAUDE.md                # Points to AGENTS.md
└── LICENSE                  # MIT License
```

## 🤝 Contributing
Feel free to open issues or submit pull requests to improve the agent!

## 📄 License
[MIT](LICENSE)
