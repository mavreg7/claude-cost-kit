#!/usr/bin/env python3
"""Usage tracker + budget guard.
  usage.py record   (Stop hook)             -> tally this session's tokens from the transcript
  usage.py check    (UserPromptSubmit hook) -> warn near budget, block prompt over budget
  usage.py report                           -> print last 7 days
Cost unit = 'weighted tokens' (input 1, cache-write 1.25, cache-read 0.1, output 5), summed over models.
Optional USD: fill $/MTok in ~/.claude/usage/pricing.json (substring of model id -> {in, out}).
"""
import datetime as dt, glob, json, os, sys

HOME = os.path.expanduser("~/.claude/usage")
SESS = os.path.join(HOME, "sessions")
os.makedirs(SESS, exist_ok=True)
today = dt.date.today().isoformat()


def load(name, default):
    try:
        return json.load(open(os.path.join(HOME, name)))
    except Exception:
        return default


def tally(transcript):
    msgs = {}
    try:
        for line in open(transcript):
            try:
                o = json.loads(line)
            except Exception:
                continue
            m = o.get("message") or {}
            if o.get("type") == "assistant" and isinstance(m.get("usage"), dict):
                msgs[m.get("id") or o.get("uuid")] = (m.get("model", ""), m["usage"])
    except OSError:
        return 0.0, 0.0
    pricing = load("pricing.json", {})
    w = usd = 0.0
    for model, u in msgs.values():
        i, cw = u.get("input_tokens", 0), u.get("cache_creation_input_tokens", 0)
        cr, out = u.get("cache_read_input_tokens", 0), u.get("output_tokens", 0)
        w += i + 1.25 * cw + 0.1 * cr + 5 * out
        for key, p in pricing.items():
            if key in model:
                usd += (i + 1.25 * cw + 0.1 * cr) * p["in"] / 1e6 + out * p["out"] / 1e6
                break
    return w, usd


def day_total():
    t = 0.0
    for f in glob.glob(os.path.join(SESS, "*.json")):
        try:
            d = json.load(open(f))
            if d.get("date") == today:
                t += d.get("weighted", 0)
        except Exception:
            pass
    return t


def fmt(n):
    return f"{n/1e6:.1f}M"


cmd = sys.argv[1] if len(sys.argv) > 1 else ""
try:
    data = json.load(sys.stdin) if not sys.stdin.isatty() and cmd != "report" else {}
except Exception:
    data = {}
sid = data.get("session_id", "unknown")

if cmd == "record":
    tp = data.get("transcript_path")
    if tp:
        w, usd = tally(tp)
        json.dump({"date": today, "weighted": w, "usd": usd},
                  open(os.path.join(SESS, f"{sid}.json"), "w"))
elif cmd == "check":
    b = load("budget.json", {"daily_limit": 40e6, "session_limit": 20e6, "warn_pct": 80})
    day = day_total()
    try:
        sess = json.load(open(os.path.join(SESS, f"{sid}.json"))).get("weighted", 0)
    except Exception:
        sess = 0
    for label, used, lim in (("daily", day, b["daily_limit"]), ("session", sess, b["session_limit"])):
        if lim and used >= lim:
            sys.stderr.write(f"Budget guard: {label} usage {fmt(used)} >= limit {fmt(lim)} weighted tokens. "
                             f"Blocked. Raise limits in ~/.claude/usage/budget.json or start a new day/session.\n")
            sys.exit(2)
    for label, used, lim in (("daily", day, b["daily_limit"]), ("session", sess, b["session_limit"])):
        if lim and used >= lim * b.get("warn_pct", 80) / 100:
            print(json.dumps({"systemMessage": f"⚠ {label} usage {fmt(used)}/{fmt(lim)} weighted tokens "
                                               f"({used/lim:.0%}). Consider /clear or wrapping up."}))
            break
elif cmd == "report":
    by = {}
    for f in glob.glob(os.path.join(SESS, "*.json")):
        try:
            d = json.load(open(f))
            by.setdefault(d["date"], [0, 0.0, 0])
            by[d["date"]][0] += d["weighted"]; by[d["date"]][1] += d.get("usd", 0); by[d["date"]][2] += 1
        except Exception:
            pass
    for day in sorted(by)[-7:]:
        w, usd, n = by[day]
        print(f"{day}  {fmt(w):>8} weighted  {n} sessions" + (f"  ~${usd:.2f}" if usd else ""))
