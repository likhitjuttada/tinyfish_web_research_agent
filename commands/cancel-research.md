---
description: "Cancel an active TinyFish research session"
allowed-tools:
  - Bash(test -f .claude/tinyfish-research.local.md *)
  - Bash(rm -f .claude/tinyfish-research.local.md .claude/tinyfish-research.lock)
  - Bash(kill *)
  - Bash(pkill *)
  - Bash(cat research/*/agent-pids.txt *)
  - Read
---

Check if a research session is active:

```bash
test -f .claude/tinyfish-research.local.md && echo "ACTIVE" || echo "NONE"
```

If active, read `.claude/tinyfish-research.local.md` to get the current phase and research ID.

Then kill any running processes and clean up:

```bash
# Read the research_id from state file
RESEARCH_ID=$(sed -n 's/^research_id: *//p' .claude/tinyfish-research.local.md | head -1)

# Kill running Python process if PID file exists
PID_FILE="research/${RESEARCH_ID}/agent-pids.txt"
if [ -f "$PID_FILE" ]; then
  for pid in $(cat "$PID_FILE"); do
    kill -TERM "$pid" 2>/dev/null || true
  done
  sleep 1
  for pid in $(cat "$PID_FILE"); do
    kill -KILL "$pid" 2>/dev/null || true
  done
  rm -f "$PID_FILE"
fi

# Remove state file and lock file
rm -f .claude/tinyfish-research.local.md .claude/tinyfish-research.lock
```

Report: "TinyFish research cancelled (was at phase: X, research ID: Y). Running processes have been terminated."

If no research session was active, report: "No active research session found."
