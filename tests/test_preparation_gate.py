"""Pre-pilot gate reports NO-GO without signed approval, regardless of green CI."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from prepilot_gate import report

class ReadinessTests(unittest.TestCase):
    def test_construction_metrics_and_human_gate(self):
        state=report()
        self.assertEqual(state["expected_main_templates_per_model"],1440)
        self.assertEqual(state["expected_pilot_templates_per_model"],144)
        self.assertEqual(state["unique_target_action_pairs_main"],15)
        self.assertFalse(state["ready_for_paid_pilot"])
        self.assertEqual(state["unsigned_semantic_approvals"],66)
        self.assertTrue(any("Pilot approval incomplete" in x for x in state["blocking_gates"]))

    def test_warning_semantic_length_mismatch(self):
        state=report()
        self.assertLess(state["control_to_target_length_ratio"],0.95)
        self.assertTrue(any("length" in x for x in state["blocking_gates"]))

if __name__=="__main__":
    unittest.main()
