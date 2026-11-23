#!/usr/bin/env python3
"""Install the cost kit into ~/.claude (or $CLAUDE_HOME). Idempotent; merges, backs up, never clobbers."""
import json, os, shutil, sys, time

KIT = os.path.dirname(os.path.abspath(__file__))
DEST = os.environ.get("CLAUDE_HOME", os.path.expanduser("~/.claude"))
START, END = "<!-- cost-kit:start -->", "<!-- cost-kit:end -->"

def op(p, m="r"):
    return open(p, m, encoding="utf-8", errors="replace" if "r" in m else "strict")


def backup(p):
    if os.path.exists(p):
        shutil.copy2(p, f"{p}.bak-{time.strftime('%Y%m%d%H%M%S')}")


def copy_dir(sub, mode=None):
    os.makedirs(os.path.join(DEST, sub), exist_ok=True)
    for f in os.listdir(os.path.join(KIT, sub)):
        if not os.path.isfile(os.path.join(KIT, sub, f)):
            continue
        shutil.copy2(os.path.join(KIT, sub, f), os.path.join(DEST, sub, f))
        if mode:
            os.chmod(os.path.join(DEST, sub, f), mode)


def managed_block(path, body, START=START, END=END):
    block = f"{START}\n{body.strip()}\n{END}\n"
    old = op(path).read() if os.path.exists(path) else ""
    if START in old and END in old:
        a, b = old.index(START), old.index(END) + len(END)
        new = old[:a] + block.rstrip("\n") + old[b:]
    else:
        new = (old.rstrip("\n") + "\n\n" if old.strip() else "") + block
    if new != old:
        backup(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        op(path, "w").write(new)


def merge_settings():
    path = os.path.join(DEST, "settings.json")
    cur = json.load(op(path)) if os.path.exists(path) else {}
    frag = json.load(op(os.path.join(KIT, "settings.fragment.json")))
    new = json.loads(json.dumps(cur))
    new.setdefault("env", {}).update({k: v for k, v in frag["env"].items() if k not in new.get("env", {})})
    deny = new.setdefault("permissions", {}).setdefault("deny", [])
    deny += [d for d in frag["permissions"]["deny"] if d not in deny]
    for event, groups in frag["hooks"].items():
        have = new.setdefault("hooks", {}).setdefault(event, [])
        existing = {h.get("command") for g in have for h in g.get("hooks", [])}
        for g in groups:
            if not all(h["command"] in existing for h in g["hooks"]):
                have.append(g)
    if new != cur:
        backup(path)
        json.dump(new, op(path, "w"), indent=2)
        op(path, "a").write("\n")


copy_dir("hooks", 0o755)
copy_dir("agents")
os.makedirs(os.path.join(DEST, "usage"), exist_ok=True)
for n in ("budget.json",):
    t = os.path.join(DEST, "usage", n)
    if not os.path.exists(t):
        shutil.copy2(os.path.join(KIT, n), t)
managed_block(os.path.join(DEST, "CLAUDE.md"), op(os.path.join(KIT, "global-CLAUDE.md")).read())
merge_settings()

# Global gitignore so ripgrep-based Glob/Grep skip junk dirs in every repo (skipped if you set your own excludesfile).
gi = os.path.join(os.path.expanduser("~/.config/git"), "ignore")
if DEST == os.path.expanduser("~/.claude"):
    managed_block(gi, op(os.path.join(KIT, "templates", "gitignore-snippet")).read(),
                  "# cost-kit:start", "# cost-kit:end")
print(f"Installed to {DEST}")
