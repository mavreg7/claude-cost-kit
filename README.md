# claude-cost-kit
Token-efficiency config for Claude Code: lean global CLAUDE.md, deny rules for junk dirs/lockfiles/logs,
Haiku subagents (`scout`, `log-summarizer`), output-trimming hook, usage tracker + budget guard.

## Install (any device)
    git clone <this repo> ~/claude-cost-kit && python3 ~/claude-cost-kit/install.py

Idempotent: merges into existing `~/.claude`, backs up changed files. Re-run after `git pull`.

## Cloud environment setup script
    if [ -d claude-cost-kit ]; then python3 claude-cost-kit/install.py; fi

## Tune
- Budget: `~/.claude/usage/budget.json` (weighted tokens; defaults are placeholders)
- USD: fill `~/.claude/usage/pricing.json` as `{"<model substring>": {"in": $/MTok, "out": $/MTok}}`
- Report: `python3 ~/.claude/hooks/usage.py report`
