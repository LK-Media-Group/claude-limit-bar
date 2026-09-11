import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT/"scripts"/(name+".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
c, config = load("collect"), load("configure")

class LimitTests(unittest.TestCase):
    def test_whitelist(self):
        payload = {"cwd":"SYNTHETIC_PRIVATE_PATH", "session_id":"SYNTHETIC_SESSION", "rate_limits":{"five_hour":{"used_percentage":23,"resets_at":1800000000,"extra":"SYNTHETIC_EXTRA"}}}
        result = c.sanitize(payload, now=1700000000)
        self.assertEqual(result, {"schema_version":1,"observed_at":1700000000,"windows":{"five_hour":{"used_percentage":23.0,"resets_at":1800000000}}})
        self.assertNotIn("SYNTHETIC", json.dumps(result))
    def test_invalid_values(self):
        for value in [True, "23", -1, 101, float("nan"), float("inf")]:
            self.assertEqual(c.sanitize({"rate_limits":{"five_hour":{"used_percentage":value,"resets_at":1800000000}}})["windows"], {})
    def test_missing_limits_not_zero(self):
        self.assertEqual(c.sanitize({})["windows"], {})
    def test_atomic_permissions(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d)/"status.json"
            c.save({}, target)
            self.assertEqual(os.stat(target).st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(target.read_text())["windows"], {})
    def test_preserve_and_restore_with_live_bridge(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            settings = root/"settings.json"
            original = {"permissions":{"allow":[]}, "statusLine":{"type":"command", "command":"printf 'existing-line'", "padding":2}}
            settings.write_text(json.dumps(original))
            config.configure("install", settings, root/"installed")
            data = json.loads(settings.read_text())
            self.assertEqual(data["permissions"], original["permissions"])
            self.assertEqual(data["statusLine"]["padding"], 2)
            bridge = subprocess.run([sys.executable, str(root/"installed/bridge.py")], input='{"cwd":"SYNTHETIC_PATH"}', text=True, capture_output=True)
            self.assertEqual(bridge.returncode, 0)
            self.assertEqual(bridge.stdout, "existing-line")
            self.assertNotIn("SYNTHETIC_PATH", (root/"installed/status.json").read_text())
            data["another_setting"] = True
            settings.write_text(json.dumps(data))
            config.configure("uninstall", settings, root/"installed")
            restored = json.loads(settings.read_text())
            self.assertEqual(restored["statusLine"], original["statusLine"])
            self.assertTrue(restored["another_setting"])
    def test_conflict_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            settings = root/"settings.json"
            config.configure("install", settings, root/"installed")
            changed = {"statusLine":{"type":"command","command":"printf changed"}}
            settings.write_text(json.dumps(changed))
            with self.assertRaises(ValueError): config.configure("uninstall", settings, root/"installed")
            self.assertEqual(json.loads(settings.read_text()), changed)
    def test_no_previous_statusline(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            settings = root/"settings.json"
            config.configure("install", settings, root/"installed")
            config.configure("install", settings, root/"installed")
            config.configure("uninstall", settings, root/"installed")
            self.assertNotIn("statusLine", json.loads(settings.read_text()))

if __name__ == "__main__": unittest.main()
