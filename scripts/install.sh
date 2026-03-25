#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
# TinyFish Research Agent — Install / Setup Checker
#
# Usage:
#   install.sh                 → check configuration, print MISSING: lines
#   install.sh --install-deps  → create venv and install Python dependencies
# ──────────────────────────────────────────────────────────────────────────
set -uo pipefail

PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${PLUGIN_ROOT}/.env"
VENV_DIR="${PLUGIN_ROOT}/.venv"

# Find a working Python 3.9+ interpreter (guards against Windows Store stubs)
resolve_python() {
  for candidate in python3 python py; do
    if command -v "$candidate" &>/dev/null; then
      if "$candidate" -c "import sys; assert sys.version_info >= (3, 9)" 2>/dev/null; then
        echo "$candidate"
        return 0
      fi
    fi
  done
  return 1
}

# ── Dependency install mode ───────────────────────────────────────────────
if [ "${1:-}" = "--install-deps" ]; then
  echo "Installing Python dependencies..."

  PY=$(resolve_python) || {
    echo "ERROR: Python 3.9+ not found. Install it from https://python.org and try again."
    exit 1
  }

  # Create venv if missing
  if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    "$PY" -m venv "$VENV_DIR"
  fi

  # Resolve pip inside venv
  if [ -f "${VENV_DIR}/Scripts/pip.exe" ]; then
    PIP="${VENV_DIR}/Scripts/pip.exe"
  else
    PIP="${VENV_DIR}/bin/pip"
  fi

  "$PIP" install --upgrade pip -q
  "$PIP" install -r "${PLUGIN_ROOT}/requirements.txt"
  echo "Dependencies installed successfully."
  exit 0
fi

# ── Configuration check mode ──────────────────────────────────────────────
MISSING=()

# Check Python
if ! resolve_python &>/dev/null; then
  echo "ERROR: Python 3.9+ not found. Install it from https://python.org"
  exit 1
fi

# Check venv / deps
if [ ! -d "$VENV_DIR" ]; then
  MISSING+=("DEPS")
fi

# Check .env exists
if [ ! -f "$ENV_FILE" ]; then
  MISSING+=("TINYFISH_API_KEY")
  MISSING+=("LLM_PROVIDER_KEY")
else
  # Check TINYFISH_API_KEY
  if ! grep -qE '^TINYFISH_API_KEY=.+' "$ENV_FILE"; then
    MISSING+=("TINYFISH_API_KEY")
  fi

  # Check at least one LLM provider key is set
  HAS_LLM=false
  grep -qE '^GOOGLE_API_KEY=.+' "$ENV_FILE"   && HAS_LLM=true
  grep -qE '^OPENAI_API_KEY=.+' "$ENV_FILE"   && HAS_LLM=true
  grep -qE '^ANTHROPIC_API_KEY=.+' "$ENV_FILE" && HAS_LLM=true
  if [ "$HAS_LLM" = false ]; then
    MISSING+=("LLM_PROVIDER_KEY")
  fi
fi

# ── Report ────────────────────────────────────────────────────────────────
if [ ${#MISSING[@]} -eq 0 ]; then
  echo "OK: TinyFish is configured and ready."
  exit 0
fi

for item in "${MISSING[@]}"; do
  echo "MISSING:${item}"
done
exit 0
