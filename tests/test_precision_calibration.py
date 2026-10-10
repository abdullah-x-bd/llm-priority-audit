"""Offline checks for mechanism-aware probability calibration."""
import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from precision_calibration import calibrate, replicate, logistic
import random
class CalibrationTests(unittest.TestCase):
    def test_logistic_bounds(self):
        self.assertGreater(logistic(-100),0)
        self.assertLess(logistic(100),1)
        self.assertAlmostEqual(logistic(0),0.5)
    def test_zero_effect_approximate_unbiased(self):
        rng=random.Random(300)
        estimates=[replicate(rng,.05,0,.8,.3,.025)[0] for _ in range(500)]
        self.assertLess(abs(sum(estimates)/len(estimates)),.015)
    def test_output_grid_and_repeatability(self):
        a=calibrate(reps=100)
        b=calibrate(reps=100)
        self.assertEqual(a,b)
        self.assertEqual(len(a["results"]),24)
        self.assertTrue(all(0<=r["approx_rejection_rate"]<=1 for r in a["results"]))
        self.assertEqual(a["distinct_action_mechanism_clusters"],15)
if __name__=="__main__":
    unittest.main()
