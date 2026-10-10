"""No paid request is implied by offline-author semantic signoff."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from prepilot_gate import report

class PreparationGateTests(unittest.TestCase):
    def test_internal_audit_is_complete_but_not_external(self):
        state=report()
        self.assertTrue(state["ready_to_implement_compatibility_runner"],state["engineering_blockers"])
        self.assertTrue(state["offline_engineering_checks_passed"])
        self.assertFalse(state["ready_for_paid_pilot"])
        self.assertFalse(state["ready_for_confirmatory_run"])
        self.assertFalse(state["external_independent_semantic_signoff"])
        self.assertEqual(state["internal_author_review_count"],66)
        self.assertEqual(state["internal_pilot_review_count"],6)
        self.assertEqual(state["main_templates_per_model"],1440)
        self.assertEqual(state["pilot_templates_per_model"],144)
    def test_lengths_and_repeated_mechanisms(self):
        state=report()
        self.assertLess(state["maximum_action_length_gap_percent"],10)
        self.assertEqual(state["distinct_main_target_action_pairs"],18)
        self.assertEqual(state["max_reuse_of_target_action_pair"],4)
        self.assertEqual(state["pilot_spend_ceiling_usd"],.75)
if __name__=="__main__":
    unittest.main()
