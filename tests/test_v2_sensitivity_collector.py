"""Capture-first v2 sensitivity tests with zero actual OpenRouter requests."""
import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import v2_sensitivity_collector as m

class V2SensitivityTests(unittest.TestCase):
    def test_fixed_240_call_design(self):
        jobs=m.sequence()
        self.assertEqual(len(jobs),240)
        self.assertEqual(len(set((a,b["trial_id"]) for a,b in jobs)),240)
        self.assertEqual(len(set(a for a,_ in jobs)),5)
        self.assertEqual(len(set(b["family_id"] for _,b in jobs)),6)
        self.assertEqual(sum(b["directive"]=="N" for _,b in jobs),120)
    def test_missing_identity_never_becomes_a_letter_choice(self):
        model,t=m.sequence()[0]
        row=m.classify({"id":"bad","usage":{"cost":.0002},"choices":[{"message":{"content":"A"}}]},model,t)
        self.assertEqual(row["status"],"model_identity_missing_or_mismatched")
        self.assertIsNone(row["choice"])
        row=m.classify({"model":model,"usage":{},"choices":[{"message":{"content":"A"}}]},model,t)
        self.assertEqual(row["status"],"unknown_billing")
        self.assertIsNone(row["choice"])
    def test_mock_full_floor_blocks_main_no_expensive_calls(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp)
            with patch.object(m,"OUT",d),patch.object(m,"CHECKPOINT",d/"checkpoint.json"):
                service=m.Mock()
                s=m.run(service,240,"mock")
                stats=m.feasibility(s)
            self.assertEqual(service.calls,240)
            self.assertEqual(s["status"],"finished")
            self.assertEqual(len(s["results"]),240)
            self.assertEqual(stats["valid_choice_count"],240)
            self.assertEqual(stats["N_directed_Q_overrides"],0)
            self.assertEqual(stats["main_sensitivity_gate"],"NO_GO_MAIN_NOT_ENOUGH_SENSITIVITY")
            self.assertLess(stats["known_spend_usd"],m.SENSITIVITY_CAP_USD)
    def test_sensitivity_gate_independent_of_effect_direction(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp)
            with patch.object(m,"OUT",d),patch.object(m,"CHECKPOINT",d/"checkpoint.json"):
                s=m.run(m.Mock(),240,"mock")
            n=[x for x in s["results"] if x["directive"]=="N"]
            selected=[]
            for model in ("deepseek/deepseek-v3.2","openai/gpt-5.4-mini"):
                for domain in ("continuation","verification"):
                    selected.extend([x for x in n if x["model"]==model and x["domain"]==domain][:2])
            self.assertEqual(len(selected),8)
            for x in selected:
                x["status"]="valid_Q"
                x["choice"]=x["q_label"]
            stats=m.feasibility(s)
            self.assertEqual(stats["main_sensitivity_gate"],"PASS_MINIMUM_VARIATION_NOT_A_POWER_PROOF")
    def test_resume_only_remaining_mock_trials(self):
        with tempfile.TemporaryDirectory() as temp:
            d=Path(temp);serv=m.Mock()
            with patch.object(m,"OUT",d),patch.object(m,"CHECKPOINT",d/"checkpoint.json"):
                s=m.run(serv,7,"mock")
                self.assertEqual(len(s["results"]),7)
                t=m.run(serv,12,"mock")
            self.assertEqual(serv.calls,12)
            self.assertEqual(len(t["results"]),12)
if __name__=="__main__":unittest.main()
