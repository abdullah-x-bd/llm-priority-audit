"""Offline design integrity checks for V3. No model endpoints or credentials."""
import sys
import unittest
from collections import Counter
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from v3_delegated_choice import (  # noqa: E402
    BASE_QUALITY, DELTAS, DOMAIN_NOTES, FRAMES, LAYOUTS,
    PATTERNS, blank_review_packet, build, load_sources,
)


class DelegatedChoiceV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = build("main")
        cls.calibration = build("calibration")

    def test_fully_factorial_main_and_calibration(self):
        self.assertEqual(len(self.main), 1200)
        self.assertEqual(len(self.calibration), 120)
        for phase, dataset, per_domain in (
            ("main", self.main, 20),
            ("calibration", self.calibration, 2),
        ):
            counts = Counter((r["domain"], r["frame"], r["q_quality_minus_n"], r["layout"])
                             for r in dataset)
            self.assertEqual(len(counts), 3 * 2 * 5 * 2)
            self.assertEqual(set(counts.values()), {per_domain})
            self.assertTrue(all(r["phase"] == f"v3_{phase}_unapproved" for r in dataset))

    def test_actions_same_between_frames_for_all_matched_cases(self):
        for dataset in (self.main, self.calibration):
            keyed = {}
            for row in dataset:
                group = (row["family_id"], row["q_quality_minus_n"], row["layout"])
                keyed.setdefault(group, {})[row["frame"]] = row
            for frames in keyed.values():
                self.assertEqual(set(frames), set(FRAMES))
                a, b = frames["salient"], frames["plain"]
                for field in ("q_label", "n_label", "order", "orientation", "q_quality",
                              "n_quality", "extra_resource_units_q", "extra_resource_units_n"):
                    self.assertEqual(a[field], b[field], field)
                self.assertNotEqual(a["request_sha256"], b["request_sha256"])
                self.assertEqual(a["system_message"], b["system_message"])

    def test_counterbalance_letter_position(self):
        for dataset in (self.main, self.calibration):
            for family in set(row["family_id"] for row in dataset):
                selected = [r for r in dataset if r["family_id"] == family
                            and r["frame"] == "salient" and r["q_quality_minus_n"] == -4]
                self.assertEqual(len(selected), 2)
                self.assertEqual(set(x["q_label"] for x in selected), {"A", "B"})
                self.assertEqual(set(x["order"] for x in selected), {"Q_N", "N_Q"})
            for domain in DOMAIN_NOTES:
                subset = [r for r in dataset if r["domain"] == domain and r["frame"] == "plain"]
                self.assertEqual(len([r for r in subset if r["orientation"] == 0]),
                                 len([r for r in subset if r["orientation"] == 1]))

    def test_numerical_tradeoffs_are_exact(self):
        for row in self.main + self.calibration:
            self.assertIn(row["q_quality_minus_n"], DELTAS)
            self.assertEqual(row["q_quality"] - row["n_quality"], row["q_quality_minus_n"])
            self.assertEqual(row["n_quality"], BASE_QUALITY)
            self.assertEqual(row["extra_resource_units_q"], 0)
            self.assertEqual(row["extra_resource_units_n"], 0)

    def test_delegation_is_not_letter_directive(self):
        for row in self.main + self.calibration:
            msg = row["user_message"].lower()
            self.assertNotIn("operator directive:", msg)
            self.assertNotIn("select action a", msg)
            self.assertNotIn("select action b", msg)
            self.assertIn("no operator", msg)
            self.assertIn("which action do you recommend", msg)
            self.assertFalse(row["approval_for_paid_collection"])
            self.assertEqual(row["external_human_review"], "NOT_SIGNED")
            self.assertEqual(row["model_requests_made"], 0)

    def test_source_independence_and_mechanisms(self):
        source_main = load_sources("main")
        source_cal = load_sources("calibration")
        self.assertEqual(len(source_main), 60)
        self.assertEqual(len(source_cal), 6)
        self.assertTrue({r["family_id"] for r in source_main}.isdisjoint(
            {r["family_id"] for r in source_cal}))
        self.assertTrue(all(not r["previous_model_choice_testing"] for r in source_cal))
        self.assertEqual(set(r["mechanism"] for r in source_main), set(PATTERNS))

    def test_no_duplicate_trial_ids_or_exact_payloads(self):
        for dataset in (self.main, self.calibration):
            self.assertEqual(len(dataset), len(set(r["trial_id"] for r in dataset)))
            self.assertEqual(len(dataset), len(set(r["request_sha256"] for r in dataset)))

    def test_blinded_reviews_are_blank(self):
        for phase, dataset, expected in (
            ("main", self.main, 120), ("calibration", self.calibration, 12)
        ):
            review = blank_review_packet(dataset, phase)
            self.assertEqual(len(review), expected)
            for row in review:
                self.assertTrue(row["prompt_X"] and row["prompt_Y"])
                self.assertNotEqual(row["prompt_X"], row["prompt_Y"])
                self.assertEqual(row["independent_reviewer_id"], "")
                self.assertEqual(row["overall_decision"], "")
                self.assertEqual(row["independent_signature_or_confirmed_email"], "")


if __name__ == "__main__":
    unittest.main()
