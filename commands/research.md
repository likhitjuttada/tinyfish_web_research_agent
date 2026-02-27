---
description: "Launch deep web research using TinyFish AI browser agents"
argument-hint: "<research topic>"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

Run the setup script to validate prerequisites and create the research workspace:

```bash
set -o noglob; bash "${CLAUDE_PLUGIN_ROOT}/scripts/setup-research.sh" $ARGUMENTS; _rc=$?; set +o noglob; (exit $_rc)
```

If setup fails (non-zero exit code), help the user fix the issue (install missing dependencies, set API keys, etc.) and DO NOT proceed further.

If setup succeeds (exit code 0), read the state file to get the research details:

```bash
cat .claude/tinyfish-research.local.md
```

Extract the research_id and workspace path (`research/<research_id>/`) from the state file. Tell the user:

1. The TinyFish research agent is now active
2. It will submit browser tasks, poll for completion with increasing intervals, and synthesize results
3. They can monitor progress with: `tail -f research/<research_id>/progress.log`
4. When all tasks complete, the final research document will be synthesized

Then **finish your response** — the Stop hook will automatically run the research pipeline. You do not need to run any additional commands.

When you are given the synthesis prompt (after the research pipeline completes), read the final report at `research/<research_id>/final-report.md` and the intermediate results in `research/<research_id>/intermediate/`. Present a summary of:

1. **Key Findings** — the most important information discovered across all sources
2. **Source Breakdown** — what each browser agent found, organized by URL
3. **Synthesis** — a coherent narrative combining all findings
4. **Open Questions** — what remains uncertain or was not fully explored
5. **Sources** — list of all URLs searched with brief descriptions
