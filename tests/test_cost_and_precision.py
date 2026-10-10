"""Offline budget/simulation interface regression tests."""
import json
import math
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from budget_stress import projected,C
from precision_mechanism_sensitivity import simulate

class CostAndPrecisionTests(unittest.TestCase):
    def test_roster_complete(self):
        self.assertEqual(len(C["models"]),5)
        self.assertEqual(len({x["id"] for x in C["models"]}),5)

    def test_low_and_high_cost_stress(self):
        self.assertFalse(projected(300,40)["exceeds_8_dollar_inference_budget"])
        self.assertTrue(projected(1000,350)["exceeds_8_dollar_inference_budget"])
        self.assertGreater(projected(1000,350)["estimated_usd"],
                           projected(500,100)["estimated_usd"])

    def test_pilot_increases_cost(self):
        self.assertGreater(projected(500,100,include_pilot=True)["estimated_usd"],
                           projected(500,100,include_pilot=False)["estimated_usd"])

    def test_simulation_stays_offline(self):
        a=simulate(.05,.03,reps=20)
        b=simulate(.05,.03,reps=20)
        self.assertEqual(a,b)
        self.assertGreaterEqual(a["mean_95pct_halfwidth_mechanism_cluster"],0)
        self.assertTrue(math.isfinite(a["mean_effect_estimate"]))

if __name__ == "__main__":
    unittest.main()
