"""Fault-injection suite for OpenRouter stage-one compatibility runner."""
import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from pilot_compatibility import (
    LIMIT, PilotStopped, run,chosen_cases,key_preflight,live_model_prices,
    parse_completion,make_reservation
)
from pilot_mock import MockTransport

PLAN=json.loads((Path(__file__).resolve().parents[1]/"config"/"pricing-assumptions.json").read_text())
MODELS=PLAN["models"]
ROSTER=[x["id"] for x in MODELS]

class CompatibilityTests(unittest.TestCase):
    def test_selected_cases_are_pilot_only(self):
        cases=chosen_cases(ROSTER)
        self.assertEqual(len(cases),5)
        self.assertEqual(len({t["family_id"] for _,t in cases}),5)
        self.assertTrue(all(int(t["family_id"].split("-")[1])>=91 for _,t in cases))

    def test_mock_end_to_end_five_calls(self):
        transport=MockTransport(PLAN)
        report=run(transport,PLAN,"mock")
        self.assertEqual(report["outcome"],"FINISHED_STAGE1")
        self.assertEqual(report["attempted"],5)
        self.assertEqual(report["completed"],5)
        self.assertEqual(len([c for c in transport.calls if c[0]=="/chat/completions"]),5)
        self.assertTrue(all(r["output_valid"] for r in report["records"]))
        for _,payload in [x for x in transport.calls if x[0]=="/chat/completions"]:
            self.assertIs(payload["provider"]["allow_fallbacks"],False)
            self.assertIn("max_price",payload["provider"])
            self.assertEqual(payload["max_tokens"],64)
            self.assertNotIn("models",payload)
            self.assertEqual(payload["usage"],{"include":True})

    def test_missing_or_excessive_key_limit_fails_before_network_call(self):
        for v in (None,100,0):
            with self.subTest(limit=v):
                m=MockTransport(PLAN,{"key":{"limit":v}})
                with self.assertRaises(PilotStopped):
                    run(m,PLAN,"mock")
                self.assertEqual(len([c for c in m.calls if c[0]=="/chat/completions"]),0)

    def test_fifty_dollar_key_is_accepted_and_local_budget_remains_small(self):
        m=MockTransport(PLAN,{"key":{"limit":50,"limit_remaining":50,"limit_reset":"monthly"}})
        report=run(m,PLAN,"mock")
        self.assertEqual(report["outcome"],"FINISHED_STAGE1")
        self.assertEqual(report["completed"],5)
        self.assertEqual(report["budget_usd"],.75)
        self.assertLessEqual(sum(row["reservation_usd"] for row in report["records"]),.75)
        self.assertLessEqual(report["reported_cost_usd"],.75)

    def test_key_insufficient_balance_not_accepted(self):
        m=MockTransport(PLAN,{"key":{"limit_remaining":.01}})
        with self.assertRaises(PilotStopped):
            run(m,PLAN,"mock")

    def test_high_catalog_price_respects_request_ceiling(self):
        price={"data":[{"id":x["id"],"pricing":{
            "prompt":str(x["input"]/1e6),
            "completion":str(x["output"]/1e6)
        }} for x in MODELS]}
        price["data"][3]["pricing"]["completion"]="0.5"
        m=MockTransport(PLAN,{"models":price})
        result=run(m,PLAN,"mock")
        self.assertEqual(result["outcome"],"FINISHED_STAGE1")
        requests=[p for path,p in m.calls if path=="/chat/completions"]
        self.assertEqual(len(requests),5)
        for payload in requests:
            model=next(x for x in MODELS if x["id"]==payload["model"])
            self.assertAlmostEqual(payload["provider"]["max_price"]["prompt"],model["input"]*1.5)
            self.assertAlmostEqual(payload["provider"]["max_price"]["completion"],model["output"]*1.5)

    def test_http200_upstream_error_is_not_called_model_swap(self):
        model,trial=chosen_cases(ROSTER)[0]
        answer={"id":"gen-synthetic-failure","error":{"code":502,"message":"upstream provider failed"}}
        with self.assertRaisesRegex(PilotStopped,"HTTP200_UPSTREAM_ERROR_ENVELOPE"):
            parse_completion(answer,model,trial)
        self.assertNotIn("model",answer)

    def test_http200_generation_id_with_no_model_is_incomplete_not_swap(self):
        model,trial=chosen_cases(ROSTER)[0]
        answer={"id":"gen-synthetic-failure"}
        with self.assertRaisesRegex(PilotStopped,"HTTP200_INCOMPLETE_MISSING_MODEL"):
            parse_completion(answer,model,trial)

    def test_http200_choice_error_is_not_accepted(self):
        model,trial=chosen_cases(ROSTER)[0]
        answer={"id":"gen-synthetic-failure","model":model,
                "usage":{"cost":0.0001},
                "choices":[{"finish_reason":"error","error":{"message":"upstream error"},
                            "message":{"content":trial["authorized_label"]}}]}
        with self.assertRaisesRegex(PilotStopped,"HTTP200_UPSTREAM_CHOICE_ERROR"):
            parse_completion(answer,model,trial)

    def test_missing_cost_stops_after_one_request(self):
        m=MockTransport(PLAN,{"completion":{"usage":{"prompt_tokens":20}}})
        r=run(m,PLAN,"mock")
        self.assertEqual(r["attempted"],1)
        self.assertEqual(r["completed"],0)
        self.assertEqual(r["outcome"],"STOP_BAD_RESPONSE_OR_BILLING")

    def test_substituted_model_stops(self):
        m=MockTransport(PLAN,{"completion":{"model":"unknown/provider"}})
        r=run(m,PLAN,"mock")
        self.assertEqual(r["attempted"],1)
        self.assertEqual(r["outcome"],"STOP_BAD_RESPONSE_OR_BILLING")

    def test_http_402_and_rate_limit_are_not_retried(self):
        for code in ("HTTP_402","HTTP_429","NETWORK_UNCERTAIN"):
            with self.subTest(code=code):
                m=MockTransport(PLAN,{"request_error":code})
                r=run(m,PLAN,"mock")
                self.assertEqual(r["attempted"],1)
                self.assertEqual(r["completed"],0)
                self.assertEqual(r["outcome"],"STOP_UNKNOWN_BILLING_AFTER_REQUEST")
                self.assertEqual(len([c for c in m.calls if c[0]=="/chat/completions"]),1)

    def test_malformed_response_recorded_without_retry(self):
        m=MockTransport(PLAN,{"completion":{"choices":[{"message":{"content":"A or B"}}]}})
        r=run(m,PLAN,"mock")
        self.assertEqual(r["completed"],5)
        self.assertFalse(all(x["output_valid"] for x in r["records"]))

    def test_reservation_at_least_three_cents(self):
        _,case=chosen_cases(ROSTER)[0]
        self.assertGreaterEqual(make_reservation(case,{"prompt":.75/1e6,"completion":4.5/1e6}),.03)

if __name__=="__main__":
    unittest.main()
