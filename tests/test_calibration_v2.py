"""The new six-family calibration set is genuinely separate and unapproved."""
import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from expand_design import load_families
from generate_calibration_v2 import build,generate,source_families
class HeldoutCalibrationTests(unittest.TestCase):
    def test_new_calibration_sources_not_in_main_or_old_pilot(self):
        new={x["family_id"] for x in source_families()}
        existing={x["family_id"] for phase in ("main","pilot")
                  for x in load_families(phase)}
        self.assertEqual(len(new),6)
        self.assertFalse(new & existing)
    def test_no_authority_reinterpretation_and_no_approval(self):
        records,review=build()
        self.assertEqual(len(records),72)
        self.assertEqual(len(review),12)
        self.assertTrue(all(not x["external_signoff"] for x in review))\n        self.assertEqual(set(x["reviewer_slot"] for x in review),{"1","2"})\n        self.assertTrue(all("version_X_action_Q" in x and "priority_Q" not in x for x in review))
        for r in records:
            self.assertIn(r["scientific_status"],("UNAPPROVED_CANDIDATE_DO_NOT_COLLECT_CONFIRMATORY",))
            if r["style"]=="concise_operator":
                self.assertEqual(r["user_message"].count("Operator directive:"),1)
            elif r["style"]=="undirected_diagnostic":
                self.assertNotIn("Operator directive:",r["user_message"])
                self.assertEqual(r["directive"],"NONE")
    def test_generator_creates_source_and_unapproved_review(self):
        with tempfile.TemporaryDirectory() as t:
            r=generate(Path(t))
            self.assertEqual(r["new_source_families"],6)
            self.assertEqual(r["unapproved_prompt_variants"],72)
            self.assertEqual(r["paid_calls"],0)
            self.assertEqual(r["reviewer_signoffs_completed"],0)
if __name__=="__main__":unittest.main()
