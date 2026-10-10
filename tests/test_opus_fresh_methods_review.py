"""Methods meta-review must be one bounded call, source-blinded, not label chasing."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import opus_fresh_methods_review as m

class MetareviewTests(unittest.TestCase):
    def test_15_pattern_selection(self):
        s=m.underlying_patterns()
        self.assertEqual(len(s),15)
        self.assertEqual(len(set((f["domain"],f["mechanism"]) for f in s)),15)
    def test_no_prior_outcomes_or_reviews(self):
        p=m.independent_prompt()
        self.assertIn("FIFTEEN BASE ACTION PATTERNS",p)
        self.assertIn("Representative FULL model-facing",p)
        self.assertNotIn("REJECT.",p)
        self.assertNotIn("0/60",p)
        self.assertNotIn("Claude Sonnet",p)
        self.assertNotIn("719",p)
        self.assertIn("causal estimand",p)
        self.assertLess(m.reserve(p),m.COST_CAP)
    def test_mock_single_call_and_duplicate_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"one-pass.json"
            with patch.object(m,"OUTFILE",path):
                service=m.Mock()
                self.assertEqual(m.execute(service,"mock"),0)
                self.assertEqual(service.calls,1)
                state=json.loads(path.read_text())
                self.assertEqual(state["status"],"completed")
                self.assertEqual(state["patterns_shown"],15)
                self.assertTrue(state["blinded_to_prior_reviews"])
                with self.assertRaisesRegex(RuntimeError,"ALREADY_ATTEMPTED"):
                    m.execute(service,"mock")
                self.assertEqual(service.calls,1)
    def test_review_only_no_experiment_runner(self):
        self.assertFalse(hasattr(m,"collect"))
        self.assertFalse(hasattr(m,"build_confirmatory_trial"))
if __name__=="__main__":unittest.main()
