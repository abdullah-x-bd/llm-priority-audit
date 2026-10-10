"""Command-line regression for pilot readiness gate."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts"/"prepilot_gate.py"

class GateCLITests(unittest.TestCase):
    def test_offline_engineering_enforce_ready(self):
        r=subprocess.run([sys.executable,str(SCRIPT),"--enforce-ready"],
                         cwd=ROOT,capture_output=True,text=True,timeout=12)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('"ready_to_implement_compatibility_runner": true',r.stdout)
    def test_paid_authorization_fails_closed(self):
        r=subprocess.run([sys.executable,str(SCRIPT),"--enforce-paid-ready"],
                         cwd=ROOT,capture_output=True,text=True,timeout=12)
        self.assertEqual(r.returncode,2,r.stderr)
        self.assertIn('"ready_for_paid_pilot": false',r.stdout)

if __name__=="__main__":
    unittest.main()
