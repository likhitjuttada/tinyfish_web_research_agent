# TinyFish Research Agent

A powerful, autonomous research agent built with **LangGraph** and **TinyFish AI**. This agent takes a research query, plans a series of targeted web searches, executes them using TinyFish's headless browser automation, and synthesizes the findings into a comprehensive research document.

## 🚀 Features

- **Autonomous Planning**: Decomposes complex research queries into actionable tasks with specific URLs and goals.
- **Headless Browser Execution**: Uses [TinyFish AI](https://tinyfish.ai) to interact with websites and extract content.
- **State-Managed Polling**: Implements a robust polling mechanism with custom backoff intervals (`[2, 2, 4, 4, 4, 6, 6, 7, 8, 8]`) to efficiently wait for browser tasks to complete.
- **Multi-LLM Support**: Supports OpenAI, Anthropic, and Google Gemini via LangChain.
- **Structured Synthesis**: Aggregates results from multiple sources into a unified Markdown report.

## 🏗️ Architecture

The agent is built using a directed acyclic graph (DAG) via LangGraph:

1.  **Planner**: Generates research tasks.
2.  **Submitter**: Submits tasks to TinyFish as asynchronous "fire-and-forget" runs.
3.  **Poller**: Periodic checks for completed runs.
4.  **Wait Node**: Implements the polling delay with backoff logic.
5.  **Synthesizer**: Finalizes the research document once all data is collected.

## 🛠️ Setup

### Prerequisites
- Python 3.9+
- A TinyFish API Key
- An LLM API Key (OpenAI, Anthropic, or Google)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/tiny-fish-research-agent.git
   cd tiny-fish-research-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file in the root directory:
   ```env
   # API Keys
   TINYFISH_API_KEY=your_tinyfish_key
   LLM_PROVIDER=google  # or openai, anthropic
   GOOGLE_API_KEY=your_google_key
   
   # Model Configuration (Optional)
   LLM_MODEL=gpt-4-turbo # if using openai
   ```

## 📖 Usage

Run the researcher from the command line:

```bash
python main.py "Your research topic here"
```

The final document will be saved in the `output/` directory as a Markdown file.

## 📁 Project Structure

- `main.py`: Entry point for the application.
- `graph.py`: Defines the LangGraph workflow and polling logic.
- `nodes/`: Contains the logic for each step (planner, executor, synthesizer).
- `models/`: Pydantic and TypedDict schemas for state management.
- `prompts/`: Text files for LLM system instructions.
- `config.py`: Configuration and environment variable loading.

## 🤝 Contributing
Feel free to open issues or submit pull requests to improve the agent!
