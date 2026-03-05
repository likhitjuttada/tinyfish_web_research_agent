#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────
# TinyFish Research Agent — Stop Hook Orchestrator
#
# This hook fires after every Claude response. It checks if a research
# session is active. The pipeline runs in the background so Claude remains
# usable while research is in progress.
#
# Flow:
#   1. First invocation (no lock): launch pipeline in background, exit 0
#   2. Pipeline running (lock alive): exit 0 — Claude stays responsive
#   3. Pipeline done (lock gone, report exists): trigger synthesis prompt
#   4. Pipeline failed (lock gone, no report): clean up state
# ──────────────────────────────────────────────────────────────────────────
set -uo pipefail

# Fail-open: on any unexpected error, allow Claude to continue
trap 'exit 0' ERR

STATE_FILE=".claude/tinyfish-research.local.md"
LOCK_FILE=".claude/tinyfish-research.lock"

log() {
  echo "[tinyfish-hook] $(date -u +%H:%M:%S) $1" >&2
}

# ── Consume stdin (required by hook protocol) ─────────────────────────────
cat > /dev/null

# ── No active session → allow exit ───────────────────────────────────────
if [ ! -f "$STATE_FILE" ]; then
  exit 0
fi

# ── Parse state file fields ──────────────────────────────────────────────
parse_field() {
  sed -n "s/^$1: *//p" "$STATE_FILE" | head -1
}

PHASE=$(parse_field "phase")
RESEARCH_ID=$(parse_field "research_id")
WORKSPACE=$(parse_field "workspace")
PLUGIN_ROOT=$(parse_field "plugin_root")

# Not in research phase → skip
if [ "$PHASE" != "research" ]; then
  exit 0
fi

# Validate research_id format
if ! echo "$RESEARCH_ID" | grep -qE '^research-[0-9]{8}-[0-9]{6}-[0-9]+$'; then
  log "ERROR: invalid research_id format: ${RESEARCH_ID}"
  rm -f "$STATE_FILE"
  exit 0
fi

# ── Staleness check: auto-clean after 3 hours ────────────────────────────
STARTED_AT=$(parse_field "started_at")
if [ -n "$STARTED_AT" ]; then
  NOW_EPOCH=$(date +%s)
  if [[ "$OSTYPE" == "darwin"* ]]; then
    STARTED_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$STARTED_AT" +%s 2>/dev/null || echo 0)
  else
    STARTED_EPOCH=$(date -d "$STARTED_AT" +%s 2>/dev/null || echo 0)
  fi
  AGE=$(( NOW_EPOCH - STARTED_EPOCH ))
  if [ "$AGE" -gt 10800 ]; then  # 3 hours
    log "WARN: stale state file (${AGE}s old), cleaning up"
    rm -f "$STATE_FILE" "$LOCK_FILE"
    exit 0
  fi
fi

# ── Extract topic ────────────────────────────────────────────────────────
TOPIC=$(awk '/^---$/ && count<2 {count++; next} count>=2' "$STATE_FILE" | sed '/^$/d')

if [ -z "$TOPIC" ]; then
  log "ERROR: no topic found in state file"
  rm -f "$STATE_FILE"
  exit 0
fi

# ── Lock helpers ─────────────────────────────────────────────────────────
is_lock_alive() {
  if [ ! -f "$LOCK_FILE" ]; then
    return 1
  fi
  local lock_pid
  lock_pid=$(cut -d: -f1 "$LOCK_FILE" 2>/dev/null || echo "")
  if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
    return 0
  fi
  return 1
}

# ── Pipeline already running in background → stay non-blocking ───────────
if is_lock_alive; then
  log "INFO: research pipeline is running in background ($(cat "$LOCK_FILE"))"
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "$0")/../scripts" && pwd)"

# ── Stale lock: pipeline finished or crashed → check results ─────────────
if [ -f "$LOCK_FILE" ]; then
  log "INFO: lock is gone, checking results"
  rm -f "$LOCK_FILE"

  if [ -f "${WORKSPACE}/final-report.md" ]; then
    # Transition state to synthesis
    if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' 's/^phase: research$/phase: synthesis/' "$STATE_FILE"
    else
      sed -i 's/^phase: research$/phase: synthesis/' "$STATE_FILE"
    fi

    INTERMEDIATE_COUNT=0
    if [ -d "${WORKSPACE}/intermediate" ]; then
      INTERMEDIATE_COUNT=$(find "${WORKSPACE}/intermediate" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
    fi

    REASON="The TinyFish research pipeline has completed for topic: ${TOPIC}. Let the user know their research is done and the report is saved at ${WORKSPACE}/final-report.md (${INTERMEDIATE_COUNT} sources). Do not read or summarize the report yourself."
    rm -f "$STATE_FILE"
    python3 -c "import json,sys; print(json.dumps({'decision': 'block', 'reason': sys.argv[1]}))" "$REASON"
  else
    log "WARN: pipeline finished but no final report found"
    rm -f "$STATE_FILE"
  fi
  exit 0
fi

# ── No lock → first invocation: launch pipeline in background ────────────
log "Launching research pipeline in background (ID: ${RESEARCH_ID})"
log "Topic: ${TOPIC}"

nohup bash "${SCRIPT_DIR}/run-research.sh" \
    "$RESEARCH_ID" \
    "$TOPIC" \
    "$PLUGIN_ROOT" \
    "$WORKSPACE" \
    >> "${WORKSPACE}/progress.log" 2>&1 &

BG_PID=$!
echo "${BG_PID}:$(date +%s)" > "$LOCK_FILE"
log "Pipeline started with PID ${BG_PID} — Claude is now free to respond"

# Allow Claude to respond immediately
exit 0
