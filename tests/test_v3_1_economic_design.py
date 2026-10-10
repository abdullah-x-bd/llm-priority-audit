"""Prospective V3.1 OFFLINE behavioral study invariants. Zero external API calls."""
from __future__ import annotations

import sys
import unittest
from collections import Counter
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0,str(SCRIPTS))

from v3_1_economic_design import (  # noqa: E402
    B_COST_LEVELS, COST_LEVELS, DELEGATED, DISPLAY_ORDERS, DOMAINS, EXPLICIT_CONTROL,
    PRESENTATIONS, PROFILES, Q_LABELS, actions_and_blocks, build,
    effort_levels, exact_expected_hundredths, independent_review_sheet, load_inventory,
    render, threshold,
)


class V31SurgicalRedesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = load_inventory()
        cls.main = build("main")
        cls.calibration = build("calibration")

    def test_source_inventory_and_factorial_counts(self):
        self.assertEqual(len(self.inventory),66)
        self.assertEqual(len(self.main),1680)
        self.assertEqual(len(self.calibration),288)
        self.assertEqual(len({r["trial_id"] for r in self.main+self.calibration}),1968)
        self.assertEqual(len({r["request_sha256"] for r in self.main+self.calibration}),1968)
        self.assertEqual(Counter(f["domain"] for f in self.inventory),
                         Counter({x:22 for x in DOMAINS}))
        for data, expected in ((self.main,60),(self.calibration,6)):
            ids = {r["family_id"] for r in data}
            self.assertEqual(len(ids),expected)
            for fid in ids:
                cases=[r for r in data if r["family_id"]==fid]
                self.assertEqual(len(cases),28 if expected==60 else 48)

    def test_domain_profiles_are_economically_coherent_and_monotone(self):
        self.assertEqual(len(PROFILES),15)
        for mechanism,p in PROFILES.items():
            t=threshold(p)
            sweep=effort_levels(p)
            self.assertEqual(len(sweep),5)
            self.assertEqual(sweep["break_even"],t)
            self.assertEqual(sweep["below_break_even"],t-2)
            self.assertEqual(sweep["above_break_even"],t+2)
            self.assertEqual(sorted(sweep.values()),list(sweep.values()))
            scores={level:exact_expected_hundredths(p,c) for level,c in sweep.items()}
            # In CONT, Q incumbent dominates on expected minutes when switching is expensive.
            # In REVR/VERF, Q preserved capability/check dominates at low process cost.
            low=scores["very_low"]
            high=scores["very_high"]
            tie=scores["break_even"]
            self.assertEqual(tie[0],tie[1],mechanism)
            if p["domain"]=="continuation":
                self.assertGreater(low[0],low[1],mechanism)
                self.assertLess(high[0],high[1],mechanism)
            else:
                self.assertLess(low[0],low[1],mechanism)
                self.assertGreater(high[0],high[1],mechanism)

    def test_full_independent_letter_and_position_cross(self):
        for data in (self.main,self.calibration):
            for family_id in set(r["family_id"] for r in data):
                for level in COST_LEVELS:
                    subset=[r for r in data if r["family_id"]==family_id
                            and r["cost_level"]==level and r["presentation"]=="time_first"
                            and r["mode"]==DELEGATED]
                    self.assertEqual(len(subset),4)
                    self.assertEqual({(r["q_label"],r["display_order"]) for r in subset},
                                     {(q,d) for q in Q_LABELS for d in DISPLAY_ORDERS})
                    self.assertEqual({r["n_label"] for r in subset},{"A","B"})

    def test_presentation_changes_only_order_of_identical_fact_blocks(self):
        for data in (self.main,self.calibration):
            d={(r["family_id"],r["cost_level"],r["q_label"],r["display_order"],r["mode"],r["presentation"]):r for r in data}
            for row in data:
                if row["presentation"]!="risk_first":
                    continue
                key=(row["family_id"],row["cost_level"],row["q_label"],row["display_order"],row["mode"],"time_first")
                a=d[key]
                b=row
                self.assertEqual(a["prefix_constant_across_order_swap"],
                                 b["prefix_constant_across_order_swap"])
                self.assertEqual(a["time_block"],b["time_block"])
                self.assertEqual(a["risk_block"],b["risk_block"])
                self.assertEqual(a["suffix_constant_across_order_swap"],
                                 b["suffix_constant_across_order_swap"])
                self.assertNotEqual(a["request_sha256"],b["request_sha256"])
                # Reconstruct content to prevent any hidden frame-specific text.
                prefix=a["prefix_constant_across_order_swap"]
                end=a["suffix_constant_across_order_swap"]
                self.assertEqual(a["user_message"],prefix+a["time_block"]+"\n\n"+a["risk_block"]+end)
                self.assertEqual(b["user_message"],prefix+b["risk_block"]+"\n\n"+b["time_block"]+end)

    def test_exact_cost_pairing_in_presentation_study(self):
        for data,contexts in ((self.main,60),(self.calibration,6)):
            ordered=[r for r in data if r["presentation"]=="risk_first"]
            self.assertEqual(len(ordered),contexts*8)
            self.assertTrue(all(r["cost_level"] in B_COST_LEVELS for r in ordered))
            self.assertTrue(all(r["mode"]==DELEGATED for r in ordered))

    def test_context_specific_names_and_release_semantics(self):
        inv={x["family_id"]:x for x in self.inventory}
        for row in self.main+self.calibration:
            content=row["user_message"]
            self.assertIn(inv[row["family_id"]]["task_object"],content)
            self.assertIn(inv[row["family_id"]]["source_title"],content)
            self.assertNotIn("Operator directive:",content)
            self.assertNotIn("planned handoff",content.lower())
            self.assertNotIn("predetermined clean",content.lower())
            self.assertNotIn("task quality (0 to 100",content.lower())
            self.assertFalse(row["paid_collection_authorized"])
            self.assertEqual(row["api_requests_made"],0)
            self.assertEqual(row["independent_human_review"],"NOT_APPROVED")
            if row["domain"]=="verification":
                # Both routes release; no inspect-versus-publish mismatch.
                line=[l for l in content.splitlines() if l.startswith(("A. ","B. "))]
                self.assertEqual(len(line),2)
                self.assertTrue(all("release the " in x for x in line))
                self.assertTrue(all(inv[row["family_id"]]["task_object"] in x for x in line))
                self.assertIn(inv[row["family_id"]]["check_target"],content)
                self.assertIn("residual error probability",content.lower())
            if row["domain"]=="reversibility":
                self.assertIn("published now under either",content)
                self.assertIn("repair labor",content)
            if row["domain"]=="continuation":
                self.assertIn("current processor is not the adviser",content)
                self.assertIn("same deliverable",content)

    def test_economic_control_has_determinate_correct_responses_and_tie(self):
        controls=[r for r in self.calibration if r["mode"]==EXPLICIT_CONTROL]
        self.assertEqual(len(controls),120)
        self.assertTrue(all(r["presentation"]=="time_first" for r in controls))
        for r in controls:
            q,n=r["expected_q_minutes_hundredths"],r["expected_n_minutes_hundredths"]
            ans="T" if q==n else (r["q_label"] if q<n else r["n_label"])
            self.assertEqual(r["arithmetic_control_correct_answer"],ans)
            if r["cost_level"]=="break_even":
                self.assertEqual(ans,"T")
            else:
                self.assertIn(ans,("A","B"))
        self.assertFalse(any(r["mode"]==EXPLICIT_CONTROL for r in self.main))

    def test_no_leaked_human_approval(self):
        self.assertEqual(len(independent_review_sheet("main")),120)
        self.assertEqual(len(independent_review_sheet("calibration")),12)
        for form in independent_review_sheet("main")+independent_review_sheet("calibration"):
            self.assertEqual(form["reviewer_identity"],"")
            self.assertEqual(form["reviewer_decision_pass_revise_reject"],"")
            self.assertTrue(form["canonical_option_Q"])
            self.assertTrue(form["canonical_option_N"])

    def test_fails_if_context_inventory_is_wrong(self):
        p=PROFILES["repeat_check"]
        self.assertEqual(threshold(p),6)
        with self.assertRaises(ValueError):
            render(self.inventory[0],"not_a_level","A","Q_N","time_first",DELEGATED,"main")
        with self.assertRaises(ValueError):
            render(self.inventory[0],"very_low","A","Q_N","time_first",EXPLICIT_CONTROL,"main")


if __name__=="__main__":
    unittest.main()
