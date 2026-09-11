#!/usr/bin/env python3
"""Installed statusLine adapter; preserve an existing user command."""
import json
from pathlib import Path
import subprocess
import sys
from collect import save

def main():
    raw = sys.stdin.buffer.read(2_000_001)
    if len(raw) > 2_000_000: return 1
    value = None
    try: value = save(json.loads(raw), Path(__file__).parent / "status.json")
    except (OSError, ValueError, TypeError): pass
    state = json.loads((Path(__file__).parent / "install-state.json").read_text())
    original = state.get("original_statusline")
    if original:
        # Only the pre-existing, locally configured command is executed. Never feed content.
        command = original["command"]
        try: return subprocess.run(command, shell=True, input=raw, timeout=10).returncode
        except subprocess.TimeoutExpired: return 1
    windows = value["windows"] if value else {}
    labels = [("five_hour", "5h"), ("seven_day", "7d")]
    print(" · ".join(f"{label} {windows[key]['used_percentage']:.0f}%" for key,label in labels if key in windows) or "Claude limity —")
    return 0

if __name__ == "__main__": sys.exit(main())
