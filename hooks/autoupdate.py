#!/usr/bin/env python3
"""SessionStart hook: keep the kit up to date. At most once per 24h: git pull the kit, re-run install.py if it changed.
Silent and fail-safe (never prints, never blocks). Disable with CLAUDE_COST_KIT_NO_UPDATE=1."""
import sys as _s
for _st in (_s.stdin, _s.stdout, _s.stderr):
    try:
        _st.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import os, subprocess, sys, time

try:
    if os.environ.get("CLAUDE_COST_KIT_NO_UPDATE"):
        sys.exit(0)
    usage = os.path.join(os.path.expanduser("~/.claude"), "usage")
    stamp = os.path.join(usage, "last_update_check")
    if os.path.exists(stamp) and time.time() - os.path.getmtime(stamp) < 24 * 3600:
        sys.exit(0)
    kit = open(os.path.join(usage, "kit_path.txt"), encoding="utf-8").read().strip()
    if not os.path.isdir(os.path.join(kit, ".git")):
        sys.exit(0)
    os.makedirs(usage, exist_ok=True)
    open(stamp, "w").write(str(time.time()))  # stamp first: a failing network never retries every session

    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    def run(*a, t=25):
        return subprocess.run(a, capture_output=True, text=True, timeout=t, creationflags=flags,
                              stdin=subprocess.DEVNULL, encoding="utf-8", errors="replace")

    before = run("git", "-C", kit, "rev-parse", "HEAD").stdout.strip()
    run("git", "-C", kit, "pull", "--ff-only", "-q")
    after = run("git", "-C", kit, "rev-parse", "HEAD").stdout.strip()
    if before and after and before != after:
        run(sys.executable, os.path.join(kit, "install.py"), t=60)
except Exception:
    pass
sys.exit(0)
