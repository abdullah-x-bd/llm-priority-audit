"""Independent v2 model review is one bounded, outcome-blinded call."""
import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import opus_v2_final_review as m
class ModelReviewTests(unittest.TestCase):
    def test_review_prompt_and_reservation(self):
        p=m.reviewer_prompt()
        self.assertIn("All 15 underlying action patterns",p)
        self.assertIn("Representative exact model-facing prompt",p)
        self.assertNotIn("719",p)
        self.assertNotIn("0/60",p)
        self.assertNotIn("REVISE",p)
        self.assertNotIn("old pilot",p.lower())
        self.assertLess(m.reserve(p),m.MAX_COST)
    def test_one_mock_call_then_reuse_blocked(self):
        with tempfile.TemporaryDirectory() as t:
            with patch.object(m,"OUT",Path(t)/"review.json"):
                self.assertEqual(m.execute(m.Mock(),"mock"),0)
                d=json.loads(m.OUT.read_text())
                self.assertEqual(d["status"],"complete")
                self.assertEqual(d["reported_cost_usd"],.1)
                with self.assertRaisesRegex(RuntimeError,"ONE_CALL_ALREADY"):
                    m.execute(m.Mock(),"mock")
if __name__=="__main__":
    unittest.main()
