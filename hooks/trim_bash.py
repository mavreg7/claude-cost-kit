#!/usr/bin/env python3
"""PreToolUse(Bash) hook: wrap known-verbose runners so output is trimmed before entering context.
Fails safe: any doubt -> do nothing."""
import json, re, sys

try:
    data = json.load(sys.stdin)
    ti = data.get("tool_input", {})
    cmd = ti.get("command", "")
except Exception:
    sys.exit(0)

RUNNERS = re.compile(
    r"(^|&&|;)\s*(npm|pnpm|yarn|bun)\s+(run\s+)?(test|build|lint|install|ci)\b"
    r"|(^|&&|;)\s*(pytest|py\.test|jest|vitest|tsc|eslint|mypy|ruff|cargo\s+(test|build|clippy)|go\s+(test|build|vet)"
    r"|mvn|gradle|\./gradlew|dotnet\s+(build|test)|make|pip\s+install)\b"
)
SKIP = re.compile(r"\||>|\btee\b|\btrim\.py\b|&\s*$|<<|\bhead\b|\btail\b")

if "\n" in cmd.strip() or not RUNNERS.search(cmd) or SKIP.search(cmd):
    sys.exit(0)

wrapped = f"set -o pipefail; {{ {cmd}\n}} 2>&1 | python3 \"$HOME/.claude/hooks/trim.py\""
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                          "updatedInput": {**ti, "command": wrapped}}}))
