#!/usr/bin/env python3
"""Trim verbose command output from stdin: head + error lines + tail. Full log saved to disk."""
import sys as _s
for _st in (_s.stdin, _s.stdout, _s.stderr):
    try:
        _st.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import os, re, sys, time, tempfile

MAX_LINES = int(os.environ.get("TRIM_MAX_LINES", "80"))
HEAD, TAIL, ERRS, LINE_CAP = 15, 40, 60, 400
pat = re.compile(r"error|fail|✗|✖|panic|exception|traceback|assert|fatal|warning:|FAILED", re.I)

lines = sys.stdin.read().splitlines()
lines = [l if len(l) <= LINE_CAP else l[:LINE_CAP] + " …[cut]" for l in lines]
if len(lines) <= MAX_LINES:
    print("\n".join(lines))
    sys.exit(0)

d = os.path.join(tempfile.gettempdir(), "claude-trim")
os.makedirs(d, exist_ok=True)
path = os.path.join(d, f"{time.strftime('%H%M%S')}-{os.getpid()}.log")
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

head, tail = lines[:HEAD], lines[-TAIL:]
mid = lines[HEAD:-TAIL]
hits = [l for l in mid if pat.search(l)]
shown = hits[:ERRS]
print("\n".join(head))
print(f"… [{len(mid)} lines omitted; {len(hits)} error-like lines, showing {len(shown)}; full log: {path}] …")
if shown:
    print("\n".join(shown))
    print("… [tail] …")
print("\n".join(tail))
