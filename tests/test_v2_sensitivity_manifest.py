"""Calibration stimuli are separate from the v2 main and v1 pilot observations."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from v2_sensitivity_manifest import cal_families,manifest
from main_v2_matched_design import source_families
from expand_design import load_families
class CalibrationV2Test(unittest.TestCase):
    def test_heldout_family_ids(self):
        f=cal_families()
        known={x["family_id"] for x in load_families("pilot")+load_families("main")}
        self.assertEqual(len(f),6)
        self.assertFalse(set(x["family_id"] for x in f)&known)
        self.assertTrue(all(not x["operator_authority"] for x in f))
    def test_exactly_48_counterbalanced_prompts(self):
        rows=manifest()
        self.assertEqual(len(rows),48)
        self.assertEqual(len({x["trial_id"] for x in rows}),48)
        self.assertEqual(len({x["request_sha256"] for x in rows}),48)
        for x in rows:
            self.assertEqual(x["condition"],"zero")
            self.assertEqual(x["user_message"].count("Operator directive:"),1)
            self.assertNotIn("This operator has final authority",x["user_message"])
            self.assertNotIn("The directive is deliberate",x["user_message"])
            self.assertEqual(x["phase"],"calibration_v2_draft")
if __name__=="__main__":unittest.main()
