#!/usr/bin/env bash
set -euo pipefail

# ── Parse arguments ───────────────────────────────────────────────────────
TOPIC="${*:-}"

if [ -z "$TOPIC" ]; then
  echo "Error: No research topic provided."
  echo "Usage: /tinyfish:research <research topic>"
  echo ""
  echo "Example: /tinyfish:research How does RLHF work?"
  exit 1
fi

# ── Check for existing session ────────────────────────────────────────────
if [ -f ".claude/tinyfish-research.local.md" ]; then
  echo "Error: A research session is already active."
  echo "Use /tinyfish:cancel-research to abort it first, or wait for it to complete."
  exit 1
fi

# ── Resolve plugin root ──────────────────────────────────────────────────
PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# ── Check dependencies ───────────────────────────────────────────────────
MISSING=()

if ! command -v python &>/dev/null && ! command -v python3 &>/dev/null; then
  MISSING+=("python3 (Python 3.9+ — https://python.org)")
fi

if ! command -v pip &>/dev/null && ! command -v pip3 &>/dev/null; then
  MISSING+=("pip (Python package manager)")
fi

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "Error: Missing required dependencies:"
  echo ""
  for dep in "${MISSING[@]}"; do
    echo "  ✗ $dep"
  done
  echo ""
  echo "Install the missing dependencies and try again."
  exit 1
fi

# ── Check for .env file ──────────────────────────────────────────────────
if [ ! -f "${PLUGIN_ROOT}/.env" ]; then
  echo "Error: No .env file found in ${PLUGIN_ROOT}"
  echo "Create a .env file with your API keys. See .env.example for reference."
  exit 1
fi

# Check for TINYFISH_API_KEY
if ! grep -q "TINYFISH_API_KEY" "${PLUGIN_ROOT}/.env" 2>/dev/null; then
  echo "Error: TINYFISH_API_KEY not found in .env file."
  echo "Add your TinyFish API key to the .env file."
  exit 1
fi

# ── Check for Python dependencies ────────────────────────────────────────
# Best-effort check — look for the venv or installed packages
if [ -d "${PLUGIN_ROOT}/.venv" ]; then
  echo "✓ Virtual environment found"
elif python -c "import langgraph" 2>/dev/null || python3 -c "import langgraph" 2>/dev/null; then
  echo "✓ Python dependencies available"
else
  echo "Warning: Python dependencies may not be installed."
  echo "Run: pip install -r ${PLUGIN_ROOT}/requirements.txt"
  echo ""
fi

# ── Generate unique research ID ──────────────────────────────────────────
RESEARCH_ID="research-$(date +%Y%m%d-%H%M%S)-$$"

# ── Create workspace ─────────────────────────────────────────────────────
WORKSPACE="research/${RESEARCH_ID}"
mkdir -p "${WORKSPACE}/intermediate"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) Setup started" > "${WORKSPACE}/progress.log"

# ── Create state file ────────────────────────────────────────────────────
mkdir -p .claude

cat > .claude/tinyfish-research.local.md <<EOF
---
research_id: ${RESEARCH_ID}
phase: research
started_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
workspace: ${WORKSPACE}
plugin_root: ${PLUGIN_ROOT}
---
${TOPIC}
EOF

# ── Report success ───────────────────────────────────────────────────────
echo ""
echo "✅ Research session created successfully!"
echo ""
echo "  Research ID:  ${RESEARCH_ID}"
echo "  Topic:        ${TOPIC}"
echo "  Workspace:    ${WORKSPACE}/"
echo ""
echo "The Stop hook will now launch the research pipeline automatically."
