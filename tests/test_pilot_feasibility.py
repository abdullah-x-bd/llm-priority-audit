"""Synthetic full-pilot summaries are not confirmatory observations."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from expand_design import build_manifest
from research_pipeline import ROSTER
from pilot_feasibility import summarize

def make(model,t,authorized=True):
    label=t["authorized_label"] if authorized else ("A" if t["authorized_label"]=="B" else "B")
    status="valid_Q" if label==t["q_label"] else "valid_N"
    return {
        "trial_id":t["trial_id"],"family_id":t["family_id"],
        "domain":t["domain"],"frame":t["frame"],
        "condition":t["condition"],"directive":t["directive"],
        "layout":t["layout"],"mechanism":t["mechanism"],
        "pairing":t["pairing"],"q_label":t["q_label"],"n_label":t["n_label"],
        "authorized_label":t["authorized_label"],"model_id":model,
        "provider_route":"OFFLINE_TEST_PROVIDER",
        "timestamp_utc":"2026-10-10T10:00:00+00:00",
        "request_sha256":t["request_sha256"],"settings_json":'{"test":true}',
        "attempt_status":status,"raw_response":label,
        "input_tokens":100,"output_tokens":1,"reasoning_tokens":0,
        "billed_cost_usd":0.0,"notes":"SYNTHETIC_NOT_EMPIRICAL",
    }
class FeasibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=[make(m,t) for m in ROSTER for t in build_manifest("pilot")]
    def test_complete_all_operator_following_triggers_floor_warning(self):
        result=summarize(self.rows)
        self.assertEqual(result["n"],720)
        self.assertEqual(result["pilot_primary_paired_comparisons"],60)
        self.assertTrue(result["priority_zero_N_floor"])
        self.assertEqual(result["total_valid_a_b_fraction"],1)
        self.assertEqual(result["directive_N_compliance_fraction"],1)
        self.assertEqual(result["pilot_primary_priority_minus_neutral_valid_Q_difference"],0)
        self.assertIn("PILOT_EXPLORATORY",result["scientific_status"])
    def test_partial_pilot_never_looks_complete(self):
        result=summarize(self.rows[:10])
        self.assertEqual(result["decision"],"STOP_INCOMPLETE_PILOT")
    def test_asymmetric_frame_effect_detectable_descriptively(self):
        rows=[x.copy() for x in self.rows]
        for r in rows:
            if r["frame"]=="priority" and r["condition"]=="zero" and r["directive"]=="N":
                r["raw_response"]=r["q_label"]
                r["attempt_status"]="valid_Q"
        result=summarize(rows)
        self.assertAlmostEqual(result["pilot_primary_priority_minus_neutral_valid_Q_difference"],1)
        self.assertFalse(result["priority_zero_N_floor"])
if __name__=="__main__":
    unittest.main()
