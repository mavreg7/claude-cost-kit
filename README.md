# claude-cost-kit
Token-efficiency config for Claude Code: lean global CLAUDE.md, deny rules for junk dirs/lockfiles/logs,
Haiku subagents (`scout`, `log-summarizer`), output-trimming hook, usage tracker + budget guard.

## Install (any device)
    git clone <this repo> ~/claude-cost-kit && python3 ~/claude-cost-kit/install.py

Idempotent: merges into existing `~/.claude`, backs up changed files. Re-run after `git pull`.

## Install on Windows (PowerShell)
PowerShell does not expand `~` in arguments to external programs, so use `$HOME`:

    git clone https://github.com/mavreg7/claude-cost-kit "$HOME\claude-cost-kit"
    python3 "$HOME\claude-cost-kit\install.py"

Update: `git -C "$HOME\claude-cost-kit" pull; python3 "$HOME\claude-cost-kit\install.py"`
Check: `python3 "$HOME\.claude\hooks\usage.py" report`

## Cloud environment setup script
    if [ -d claude-cost-kit ]; then python3 claude-cost-kit/install.py; fi

## Tune
- Budget: `~/.claude/usage/budget.json` (weighted tokens; defaults are placeholders)
- USD: fill `~/.claude/usage/pricing.json` as `{"<model substring>": {"in": $/MTok, "out": $/MTok}}`
- Report: `python3 ~/.claude/hooks/usage.py report`
