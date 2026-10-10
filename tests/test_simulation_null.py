"""The simulated sharp null must set treatment and control probabilities equal."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from precision_mechanism_sensitivity import simulate

class SimulationSharpNullTests(unittest.TestCase):
    def test_zero_effect_is_not_clipping_generated_treatment(self):
        # The intended null has identical probabilities before each Bernoulli draw.
        # With 100 planning replications, mean estimates may deviate because of sampling.
        x=simulate(base=.01,effect=0,reps=100)
        self.assertLess(abs(x["mean_effect_estimate"]), 0.03)
        self.assertEqual(x["assumed_frame_effect"],0)

if __name__=="__main__":
    unittest.main()
