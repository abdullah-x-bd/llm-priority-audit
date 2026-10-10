"""Pilots with provider failures must report their incomplete outcomes explicitly."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from full_pilot import sample_plan,STAGE1_COST
from pilot_collection_audit import summarize
class CollectionAuditTests(unittest.TestCase):
    def test_reject_incomplete_attempt_coverage(self):
        a=summarize({"collected":[],"cost_usd":0.0,"rejected_attempts":[],"inflight":None})
        self.assertEqual(a["collection_state"],"INCOMPLETE_ATTEMPT_COVERAGE")
    def test_reject_budget_above_limit(self):
        with self.assertRaisesRegex(ValueError,"PILOT_BUDGET_OVER_CAP"):
            summarize({"collected":[],"cost_usd":0.0,
               "rejected_attempts":[{"inflight":{"reservation_usd":.76}}],
               "inflight":None})
    def test_no_inferred_valid_choices_from_unresolved(self):
        from research_pipeline import get_manifest
        _,plan=sample_plan()
        model,trial=plan[0]
        from raw_capture import unresolved_trial
        row=unresolved_trial(model,trial,{"model":model},"HTTP200_ERROR")
        a=summarize({"collected":[row],"cost_usd":0.0,
                     "rejected_attempts":[{"inflight":{"reservation_usd":.03}}],
                     "inflight":None})
        self.assertEqual(a["valid_A_B_responses"],0)
        self.assertEqual(a["unresolved_or_invalid_rows"],1)
        self.assertGreater(a["worst_case_local_pilot_liability_usd"],STAGE1_COST)
if __name__=="__main__":
    unittest.main()
