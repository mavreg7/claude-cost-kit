# Token efficiency (global)
- Path known → Read it directly (use offset/limit for big files). Never read whole large files "to look around".
- No repo-wide Glob/Grep when a dir is known; scope by directory + glob/type. Don't re-read files already in context.
- Open-ended search/exploration (>3 lookups, location unknown) → delegate to the `scout` subagent (Haiku); expect paths + short summary back.
- Verbose commands (tests, builds, linters, installs, logs) → output is auto-trimmed by hook; otherwise pipe through `python3 ~/.claude/hooks/trim.py`. Prefer `git log --oneline -n 20`, `git diff --stat`.
- Long outputs: summarize, never paste back. Don't recap diffs; keep replies short.
- Never open node_modules, dist, build, Library, Temp, lockfiles, *.log, *.min.*, *.map, generated code.
- Don't re-run checks that already passed. Fix by smallest edit.
- Unrelated new task → suggest `/clear`. Don't change model/effort mid-session (breaks prompt cache); delegate cheap work to subagents instead.
- Heavy model for: architecture, multi-file reasoning, debugging. Cheap model for: search, formatting, log triage.
