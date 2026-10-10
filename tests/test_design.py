"""Deterministic test coverage for study-design scaffolding; never calls models."""
import collections
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from expand_design import load_families, build_manifest, label_assignment
from validate_scenarios import audit

class DesignTests(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(load_families("main")), 60)
        self.assertEqual(len(load_families("pilot")), 6)
        self.assertEqual(len(build_manifest("main")), 720)
        self.assertEqual(len(build_manifest("pilot")), 72)

    def test_factorial_coverage_and_checks(self):
        for phase in ("main", "pilot"):
            report = audit(phase)
            self.assertFalse(report["validation_errors"])

    def test_label_balance(self):
        for phase, expected_each in (("main", 10), ("pilot", 1)):
            families = load_families(phase)
            mapping = label_assignment(families)
            for domain in ("continuation", "reversibility", "verification"):
                counts = collections.Counter(mapping[x["family_id"]] for x in families
                                             if x["domain"] == domain)
                self.assertEqual(counts["A"], expected_each)
                self.assertEqual(counts["B"], expected_each)

    def test_manifest_reproducible(self):
        self.assertEqual(build_manifest("main"), build_manifest("main"))

    def test_quality_manipulation(self):
        for family in load_families("main") + load_families("pilot"):
            o = family["outcomes"]
            self.assertEqual([o[k]["q_quality"] - o[k]["n_quality"]
                              for k in ("positive", "zero", "negative")],
                             [10, 0, -10])

if __name__ == "__main__":
    unittest.main()
