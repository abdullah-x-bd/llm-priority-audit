"""Offline-only scientific evaluation and blinded review packet regression."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from expand_design import build_manifest
from pilot_scientific_diagnostics import summarize
from propose_instruction_variants import variants
from generate_blind_review import generate,make_rows

class ReviewAndStimulusTests(unittest.TestCase):
    def test_review_packet_covers_60_main_six_practice(self):
        prompts,key=make_rows()
        self.assertEqual(len(prompts),66)
        self.assertEqual(len(key),66)
        self.assertEqual(len({p["family_id"] for p in prompts}),66)
        self.assertEqual(sum(x["phase"]=="external_main_review" for x in prompts),60)
        self.assertEqual(sum(x["phase"]=="practice_pilot" for x in prompts),6)
        for p in prompts:
            self.assertNotIn("frame=",p["version_X_prompt"])
            self.assertNotIn("version_X_actual_frame",p)
            self.assertNotEqual(p["version_X_sha256"],p["version_Y_sha256"])
            self.assertEqual(p["version_X_prompt"].count("Operator directive: Select action "),1)
            self.assertEqual(p["version_Y_prompt"].count("Operator directive: Select action "),1)
    def test_empty_independent_review_never_claims_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            result=generate(Path(temp))
            self.assertEqual(result["blank_main_reviewer_slots"],120)
            self.assertEqual(result["external_reviewer_signoffs_completed"],0)
            rows=list(csv.DictReader((Path(temp)/"blank-reviewer-ratings.csv").open()))
            self.assertEqual(len(rows),120)
            self.assertTrue(all(not r["actual_reviewer_id"] and
                                not r["overall_decision"] for r in rows))
            self.assertTrue((Path(temp)/"do-not-send-unblinding-key.csv").exists())
    def test_variants_preserve_old_strict_hashes(self):
        old=build_manifest("pilot")
        revised=variants("pilot",["strict_baseline"])
        self.assertEqual(len(old),144)
        self.assertEqual(len(revised),144)
        for a,b in zip(old,revised):
            self.assertEqual(a["request_sha256"],b["stimulus_sha256"])
            self.assertEqual(a["user_message"],b["user_message"])
    def test_concise_variant_is_unambiguous_but_less_redundant(self):
        new=variants("pilot",["concise_operator"])
        self.assertEqual(len(new),144)
        for x in new:
            self.assertNotEqual(x["stimulus_sha256"],x["orig_v1_sha256"])
            self.assertIn("Operator directive: Select action ",x["user_message"])
            self.assertNotIn("The directive is deliberate",x["user_message"])
            self.assertNotIn("This operator has final authority",x["user_message"])
            self.assertEqual(x["scientific_status"],
                             "UNAPPROVED_CANDIDATE_DO_NOT_COLLECT_CONFIRMATORY")
    def test_undirected_diagnostic_cannot_count_as_operator_override(self):
        rows=variants("pilot",["undirected_diagnostic"])
        self.assertEqual(len(rows),144)
        for r in rows:
            self.assertEqual(r["directive"],"NONE")
            self.assertNotIn("Operator directive:",r["user_message"])
            self.assertNotIn("operator has final authority",r["user_message"])
            self.assertIn("Select the action you recommend",r["user_message"])
    def test_scientific_audit_requires_every_manifest_cell(self):
        with self.assertRaisesRegex(ValueError,"EXPECTED_ALL_720"):
            summarize([])

if __name__=="__main__":unittest.main()
