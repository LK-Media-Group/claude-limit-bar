#!/usr/bin/env python3
"""Install/remove a statusLine bridge, preserving unrelated settings."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
import tempfile

def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temp = stream.name
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temp, path)
    finally:
        if temp and os.path.exists(temp): os.unlink(temp)

def configure(action, settings, destination):
    data = json.loads(settings.read_text()) if settings.exists() else {}
    if not isinstance(data, dict): raise ValueError("Invalid settings")
    state_path = destination / "install-state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else None
    if action == "install":
        if state:
            if data.get("statusLine") != state["installed_statusline"]:
                raise ValueError("StatusLine changed after installation; review settings manually")
            print("Already installed; existing configuration preserved.")
            return
        original = data.get("statusLine")
        if original is not None and (not isinstance(original, dict) or original.get("type") != "command" or not isinstance(original.get("command"), str)):
            raise ValueError("Unsupported existing statusLine; no settings changed")
        destination.mkdir(parents=True, exist_ok=True, mode=0o700)
        if settings.exists():
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            backup = destination / ("settings-backup-" + stamp + ".json")
            atomic(backup, data)
        for filename in ("collect.py", "bridge.py"):
            shutil.copyfile(Path(__file__).parent / filename, destination / filename)
            (destination / filename).chmod(0o600)
        installed = dict(original or {})
        installed.update(type="command", command=shlex.quote(sys.executable) + " " + shlex.quote(str(destination / "bridge.py")))
        state = {"original_statusline":original, "had_statusline":"statusLine" in data, "installed_statusline":installed}
        atomic(state_path, state)
        data["statusLine"] = installed
        try: atomic(settings, data)
        except OSError:
            state_path.unlink(missing_ok=True)
            raise
        print("Installed. Other settings and the previous statusLine command were preserved.")
    else:
        if not state: raise ValueError("No installation state found")
        if data.get("statusLine") != state["installed_statusline"]:
            raise ValueError("StatusLine changed after installation; refusing to overwrite it")
        if state["had_statusline"]: data["statusLine"] = state["original_statusline"]
        else: data.pop("statusLine", None)
        atomic(settings, data)
        state_path.unlink()
        print("Original statusLine restored. Local backups and snapshots remain on this computer.")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["install", "uninstall"])
    p.add_argument("--settings", type=Path, default=Path.home()/".claude/settings.json")
    p.add_argument("--destination", type=Path, default=Path.home()/"Library/Application Support/ClaudeLimitBar")
    args = p.parse_args()
    try:
        configure(args.action, args.settings.expanduser().resolve(), args.destination.expanduser().resolve())
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        # Avoid printing file content, original commands or user paths.
        print("Configuration unchanged or incomplete. Check valid settings and statusLine conflicts; see README.", file=sys.stderr)
        return 1

if __name__ == "__main__": sys.exit(main())
