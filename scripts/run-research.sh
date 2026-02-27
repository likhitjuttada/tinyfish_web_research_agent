#!/usr/bin/env bash
set -euo pipefail

# ── Arguments ─────────────────────────────────────────────────────────────
RESEARCH_ID="$1"
TOPIC="$2"
PLUGIN_ROOT="$3"
WORKSPACE="$4"

LOG_FILE="${WORKSPACE}/progress.log"

log() {
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $1" >> "$LOG_FILE"
  echo "$1"
}

# ── Resolve Python ────────────────────────────────────────────────────────
if [ -f "${PLUGIN_ROOT}/.venv/Scripts/python.exe" ]; then
  PYTHON="${PLUGIN_ROOT}/.venv/Scripts/python.exe"
elif [ -f "${PLUGIN_ROOT}/.venv/bin/python" ]; then
  PYTHON="${PLUGIN_ROOT}/.venv/bin/python"
elif command -v python3 &>/dev/null; then
  PYTHON="python3"
else
  PYTHON="python"
fi

log "Using Python: ${PYTHON}"

# ── Run the research pipeline ─────────────────────────────────────────────
log "Starting research pipeline for: ${TOPIC}"

# Save PID for cancellation
echo "$$" > "${WORKSPACE}/agent-pids.txt"

cd "${PLUGIN_ROOT}"

# Run main.py and capture output
if ${PYTHON} main.py "${TOPIC}" >> "$LOG_FILE" 2>&1; then
  log "Research pipeline completed successfully"
else
  EXIT_CODE=$?
  log "Research pipeline failed with exit code ${EXIT_CODE}"
  exit ${EXIT_CODE}
fi

# ── Copy results to workspace ─────────────────────────────────────────────
# Copy the final output document to the workspace
OUTPUT_DIR="${PLUGIN_ROOT}/output"
if [ -d "$OUTPUT_DIR" ]; then
  for f in "${OUTPUT_DIR}"/*.md; do
    if [ -f "$f" ]; then
      cp "$f" "${WORKSPACE}/final-report.md"
      log "Final report copied to ${WORKSPACE}/final-report.md"
      break
    fi
  done
fi

# Copy intermediate results to workspace
INTERMEDIATE_DIR="${PLUGIN_ROOT}/intermediate_results"
if [ -d "$INTERMEDIATE_DIR" ]; then
  cp "${INTERMEDIATE_DIR}"/*.json "${WORKSPACE}/intermediate/" 2>/dev/null || true
  log "Intermediate results copied to ${WORKSPACE}/intermediate/"
fi

# Clean up PID file
rm -f "${WORKSPACE}/agent-pids.txt"

log "All results saved to ${WORKSPACE}/"
