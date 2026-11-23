#!/usr/bin/env python3
"""Print a compact health report for the cost kit. Safe: read-only, prints no secrets (env var values are not shown)."""
import sys as _s
for _st in (_s.stdout, _s.stderr):
    try:
        _st.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import json, os, platform, shutil, subprocess, sys

home = os.path.expanduser("~")
cfg_env = os.environ.get("CLAUDE_CONFIG_DIR")
dest = cfg_env or os.path.join(home, ".claude")
ok = lambda c: "OK  " if c else "FAIL"
print(f"os={platform.system()} python={sys.version.split()[0]} exe={sys.executable}")
print(f"home={home}")
print(f"CLAUDE_CONFIG_DIR={'<unset>' if not cfg_env else cfg_env}  -> Claude reads config from: {dest}")
if cfg_env and os.path.abspath(cfg_env) != os.path.abspath(os.path.join(home, '.claude')):
    print(f"WARN  CLAUDE_CONFIG_DIR differs from ~/.claude: the kit was installed to ~/.claude but Claude reads {cfg_env}")

def find_bash():
    b = shutil.which("bash")
    if b:
        return b
    g = shutil.which("git")  # Git for Windows: <root>\\cmd\\git.exe, bash lives in <root>\\bin (not on PATH by default; Claude finds it itself)
    if g:
        root = os.path.dirname(os.path.dirname(g))
        for rel in ("bin/bash.exe", "usr/bin/bash.exe"):
            p = os.path.join(root, rel)
            if os.path.exists(p):
                return p
    return None

for t in ("python3", "python", "git", "claude"):
    print(f"{ok(shutil.which(t))} on PATH: {t} -> {shutil.which(t)}")
BASH = find_bash()
print(f"{ok(BASH)} bash (Git Bash is enough, PATH not required): {BASH}")

print("--- files in", dest)
for rel in ("settings.json", "CLAUDE.md", "hooks/trim.py", "hooks/trim_bash.py", "hooks/usage.py", "hooks/autoupdate.py",
            "agents/scout.md", "agents/log-summarizer.md", "usage/kit_path.txt", "usage/budget.json"):
    print(f"{ok(os.path.exists(os.path.join(dest, rel)))} {rel}")

def load(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception as e:
        return f"<{type(e).__name__}: {e}>"

print("--- settings files that Claude merges")
cands = [os.path.join(dest, "settings.json"), os.path.join(dest, "settings.local.json"),
         os.path.join(os.getcwd(), ".claude", "settings.json"), os.path.join(os.getcwd(), ".claude", "settings.local.json"),
         r"C:\Program Files\ClaudeCode\managed-settings.json", "/etc/claude-code/managed-settings.json",
         "/Library/Application Support/ClaudeCode/managed-settings.json"]
for p in cands:
    if not os.path.exists(p):
        continue
    s = load(p)
    if isinstance(s, str):
        print(f"BAD   {p}: {s}")
        continue
    hooks = s.get("hooks", {})
    print(f"found {p}")
    print(f"      hooks={ {k: len(v) for k, v in hooks.items()} } deny={len(s.get('permissions', {}).get('deny', []))} "
          f"env={sorted(s.get('env', {}))}")
    for k in ("disableAllHooks", "allowManagedHooksOnly", "allowedHttpHookUrls"):
        if k in s:
            print(f"      WARN {k}={s[k]}")

print("--- dry run of the hook commands (as the shell would run them)")
sh = BASH
for name, stdin in (("usage.py", '{"session_id":"diag"}'), ("trim_bash.py", '{"tool_input":{"command":"ls"}}')):
    arg = ["check"] if name == "usage.py" else []
    try:
        r = subprocess.run([sh or "bash", "-c", f'python3 "$HOME/.claude/hooks/{name}" {" ".join(arg)}'], input=stdin,
                           capture_output=True, text=True, timeout=20, encoding="utf-8", errors="replace")
        print(f"{ok(r.returncode == 0)} via bash: hooks/{name} rc={r.returncode} {r.stderr.strip()[:200]}")
    except Exception as e:
        print(f"FAIL via bash: hooks/{name}: {type(e).__name__}: {e}")
print("--- usage report")
subprocess.run([sys.executable, os.path.join(dest, "hooks", "usage.py"), "report"])
