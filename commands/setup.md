---
description: "Configure TinyFish research agent (API keys, dependencies)"
allowed-tools:
  - Bash
  - Read
  - Write
---

Run the setup script and capture its output:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/install.sh"
```

The script will print one of three outcomes:

1. **Already configured** — tell the user setup is already complete and they can start researching with `/tinyfish-research:research <topic>`.

2. **Needs configuration** — the script prints a list of missing items prefixed with `MISSING:`. For each one:
   - `MISSING:TINYFISH_API_KEY` — ask the user for their TinyFish API key (from tinyfish.io), then write it to `${CLAUDE_PLUGIN_ROOT}/.env` as `TINYFISH_API_KEY=<value>`
   - `MISSING:LLM_PROVIDER_KEY` — ask the user which LLM provider they want (google, openai, or anthropic) and their API key for it, then append the appropriate line to `.env`:
     - google → `GOOGLE_API_KEY=<value>` and `LLM_PROVIDER=google` and `LLM_MODEL=gemini-1.5-flash`
     - openai → `OPENAI_API_KEY=<value>` and `LLM_PROVIDER=openai` and `LLM_MODEL=gpt-4o`
     - anthropic → `ANTHROPIC_API_KEY=<value>` and `LLM_PROVIDER=anthropic` and `LLM_MODEL=claude-sonnet-4-6`
   - `MISSING:DEPS` — run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/install.sh" --install-deps` and show output

   After writing all missing values, re-run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/install.sh"` to confirm everything passes.

3. **Error** — report the error to the user and suggest they file an issue at the repository.

Once all checks pass, tell the user setup is complete and they can start with `/tinyfish-research:research <topic>`.
