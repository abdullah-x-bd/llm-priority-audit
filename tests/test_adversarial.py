"""Pre-pilot independent negative-case, metamorphic and template-integrity tests.

All tests are offline. Mutation tests must fail deliberately corrupted scenarios.
"""
import copy
import hashlib
import json
import random
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from expand_design import (
    ROOT, build_manifest, load_families, display_mapping,
    LAYOUTS, FRAMES, LEVELS, DIRECTIVES
)
from validate_scenarios import audit

class NegativeMutationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / "data" / "scenarios", self.root / "data" / "scenarios")
        shutil.copytree(ROOT / "data" / "pilot", self.root / "data" / "pilot")

    def tearDown(self):
        self.temp.cleanup()

    def corrupt_first_main(self, mutation):
        path = self.root / "data" / "scenarios" / "continuation.jsonl"
        rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines()]
        mutation(rows)
        path.write_text("\n".join(json.dumps(x) for x in rows) + "\n", encoding="utf-8")
        return audit("main", root=self.root)["errors"]

    def test_payoff_increase_detected(self):
        err = self.corrupt_first_main(
            lambda x: x[0]["outcomes"]["positive"].update({"q_quality": 99}))
        self.assertTrue(err)
        self.assertTrue(any("wrong contrast" in e for e in err))

    def test_cost_mismatch_detected(self):
        err = self.corrupt_first_main(
            lambda x: x[0]["outcomes"]["zero"].update({"q_extra_cost": 1}))
        self.assertTrue(any("parity cost violated" in e for e in err))

    def test_neutral_actions_identical_detected(self):
        err = self.corrupt_first_main(
            lambda x: x[0].update({"neutral_action_q": x[0]["neutral_action_n"]}))
        self.assertTrue(any("action descriptions missing or duplicated" in e for e in err))

    def test_duplicate_family_id_detected(self):
        err = self.corrupt_first_main(
            lambda x: x[1].update({"family_id": x[0]["family_id"]}))
        self.assertTrue(any("Duplicate family_id" in e for e in err))

    def test_unknown_field_detected(self):
        err = self.corrupt_first_main(
            lambda x: x[0].update({"unknown_treatment": True}))
        self.assertTrue(any("wrong scenario fields" in e for e in err))

    def test_mechanism_imbalance_detected(self):
        err = self.corrupt_first_main(
            lambda x: x[0].update({"mechanism": "unexpected"}))
        self.assertTrue(any("mechanisms" in e or "contexts" in e for e in err))

    def test_false_approval_detected(self):
        err = self.corrupt_first_main(
            lambda x: x[0]["quality_review"].update({"approved_for_pilot": True}))
        self.assertTrue(any("approved without independent clarity review" in e for e in err))

class PromptMetamorphicTests(unittest.TestCase):
    def test_within_family_crossing_complete(self):
        for phase in ("main", "pilot"):
            by_family = {}
            for t in build_manifest(phase):
                by_family.setdefault(t["family_id"], []).append(t)
            for family, trials in by_family.items():
                self.assertEqual(len(trials), 24)
                self.assertEqual({(t["frame"],t["condition"],t["directive"],t["layout"]) for t in trials},
                    {(f,v,d,l) for f in FRAMES for v in LEVELS for d in DIRECTIVES for l in LAYOUTS})

    def test_frame_intervention_is_only_action_description(self):
        for phase in ("main","pilot"):
            families = {f["family_id"]: f for f in load_families(phase)}
            by = {(r["family_id"],r["condition"],r["directive"],r["layout"],r["frame"]):r
                  for r in build_manifest(phase)}
            for fid, family in families.items():
                for level in LEVELS:
                    for directive in DIRECTIVES:
                        for layout in LAYOUTS:
                            a = by[fid,level,directive,layout,"priority"]
                            b = by[fid,level,directive,layout,"neutral"]
                            text = a["user_message"]
                            text = text.replace(family["action_q"], "__Q__").replace(family["action_n"], "__N__")
                            control = b["user_message"].replace(family["neutral_action_q"], "__Q__").replace(family["neutral_action_n"], "__N__")
                            self.assertEqual(text, control,
                              f"Non-description framing leakage: {fid}/{level}/{directive}/{layout}")

    def test_letter_position_pairing_manually(self):
        expected = {
            (0,"layout0"): ("A","B",("Q","N")),
            (0,"layout1"): ("B","A",("N","Q")),
            (1,"layout0"): ("B","A",("Q","N")),
            (1,"layout1"): ("A","B",("N","Q")),
        }
        for key,value in expected.items():
            self.assertEqual(display_mapping(*key), value)

    def test_prompt_hash_distinguishes_treatment(self):
        for phase in ("main","pilot"):
            trials = build_manifest(phase)
            self.assertEqual(len({t["request_sha256"] for t in trials}), len(trials))
            self.assertEqual(trials, build_manifest(phase))

    def test_no_main_pilot_overlap(self):
        main = load_families("main")
        pilot = load_families("pilot")
        for attr in ("family_id", "title", "context"):
            self.assertFalse({x[attr] for x in main}.intersection({x[attr] for x in pilot}))

if __name__ == "__main__":
    unittest.main()
