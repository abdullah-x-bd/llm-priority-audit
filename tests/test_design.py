"""Offline regression tests for matched semantic-frame factorial protocol."""
import collections
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from expand_design import load_families, build_manifest, layout_assignment, display_mapping
from validate_scenarios import audit

class DesignTests(unittest.TestCase):
    def test_counts_and_factorials(self):
        self.assertEqual(len(load_families("main")), 60)
        self.assertEqual(len(load_families("pilot")), 6)
        self.assertEqual(len(build_manifest("main")), 1440)
        self.assertEqual(len(build_manifest("pilot")), 144)
        for phase in ("main", "pilot"):
            self.assertFalse(audit(phase)["errors"])

    def test_letter_position_balance(self):
        for phase, n in (("main", 10), ("pilot", 1)):
            families = load_families(phase)
            mapping = layout_assignment(families)
            for domain in ("continuation", "reversibility", "verification"):
                counts = collections.Counter(mapping[f["family_id"]] for f in families
                                             if f["domain"] == domain)
                self.assertEqual(counts[0], n)
                self.assertEqual(counts[1], n)
        for pairing in (0, 1):
            labels = [display_mapping(pairing, layout)[0]
                      for layout in ("layout0", "layout1")]
            self.assertEqual(set(labels), {"A", "B"})

    def test_parity_and_dominance(self):
        for f in load_families("main") + load_families("pilot"):
            pay = f["outcomes"]
            for level, diff in (("positive", 10), ("zero", 0), ("negative", -10)):
                self.assertEqual(pay[level]["q_quality"] - pay[level]["n_quality"], diff)
                self.assertEqual(pay[level]["q_extra_cost"], pay[level]["n_extra_cost"])
            self.assertEqual(set(f["quality_review"].values()) >= {False, True}, True)

    def test_reproducible(self):
        self.assertEqual(build_manifest("pilot"), build_manifest("pilot"))

    def test_frame_isolation(self):
        rows = build_manifest("pilot")
        by = {(r["family_id"],r["condition"],r["directive"],r["layout"],r["frame"]):r for r in rows}
        for f in load_families("pilot"):
            for level in ("positive", "zero", "negative"):
                for d in ("Q", "N"):
                    for l in ("layout0", "layout1"):
                        a=by[(f["family_id"],level,d,l,"priority")]
                        b=by[(f["family_id"],level,d,l,"neutral")]
                        self.assertEqual(a["q_label"],b["q_label"])
                        self.assertEqual(a["n_label"],b["n_label"])
                        self.assertEqual(a["authorized_label"],b["authorized_label"])
                        self.assertNotEqual(a["user_message"],b["user_message"])

if __name__ == "__main__":
    unittest.main()
