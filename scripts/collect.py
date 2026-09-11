#!/usr/bin/env python3
"""Whitelist only aggregate limits from Claude Code statusLine stdin."""
import argparse
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time

DEFAULT = Path.home() / "Library/Application Support/ClaudeLimitBar/status.json"

def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

def sanitize(payload, now=None):
    if not isinstance(payload, dict): raise ValueError("Expected JSON object")
    result = {"schema_version":1, "observed_at":int(time.time() if now is None else now), "windows":{}}
    limits = payload.get("rate_limits")
    if not isinstance(limits, dict): return result
    for name in ("five_hour", "seven_day"):
        window = limits.get(name)
        if not isinstance(window, dict): continue
        pct, reset = window.get("used_percentage"), window.get("resets_at")
        if number(pct) and 0 <= pct <= 100 and number(reset) and 0 < reset < 10**12:
            result["windows"][name] = {"used_percentage":float(pct), "resets_at":int(reset)}
    return result

def save(payload, target=DEFAULT):
    value = sanitize(payload)
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    filename = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, prefix=".snapshot-", delete=False) as stream:
            filename = stream.name
            json.dump(value, stream, allow_nan=False)
            stream.write("\n")
        os.replace(filename, target)
    finally:
        if filename and os.path.exists(filename): os.unlink(filename)
    return value

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=DEFAULT)
    p.add_argument("--demo", action="store_true", help="Write synthetic values, never query an account")
    args = p.parse_args()
    try:
        if args.demo:
            now = time.time()
            payload = {"rate_limits":{"five_hour":{"used_percentage":23,"resets_at":now+7200},"seven_day":{"used_percentage":61,"resets_at":now+172800}}}
        else:
            raw = sys.stdin.buffer.read(2_000_001)
            if len(raw) > 2_000_000: raise ValueError("Input too large")
            payload = json.loads(raw)
        save(payload, args.output)
        return 0
    except (OSError, ValueError, TypeError):
        print("Limit snapshot unavailable; input was not logged.", file=sys.stderr)
        return 1

if __name__ == "__main__": sys.exit(main())
