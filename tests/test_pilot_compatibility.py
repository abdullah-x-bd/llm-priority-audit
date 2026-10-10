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
            self.assertEqual(payload["max_tokens"],64)
            self.assertNotIn("models",payload)
            self.assertEqual(payload["usage"],{"include":True})

    def test_missing_key_limit_fails_before_network_call(self):
        for v in (None,1,100,0):
            with self.subTest(limit=v):
                m=MockTransport(PLAN,{"key":{"limit":v}})
                with self.assertRaises(PilotStopped):
                    run(m,PLAN,"mock")
                self.assertEqual(len([c for c in m.calls if c[0]=="/chat/completions"]),0)

    def test_resetting_key_limit_not_accepted(self):
        m=MockTransport(PLAN,{"key":{"limit_reset":"daily"}})
        with self.assertRaises(PilotStopped):
            run(m,PLAN,"mock")

    def test_key_insufficient_balance_not_accepted(self):
        m=MockTransport(PLAN,{"key":{"limit_remaining":.01}})
        with self.assertRaises(PilotStopped):
            run(m,PLAN,"mock")

    def test_price_change_rejected(self):
        price={"data":[{"id":x["id"],"pricing":{
            "prompt":str(x["input"]/1e6),
            "completion":str(x["output"]/1e6)
        }} for x in MODELS]}
        price["data"][0]["pricing"]["completion"]="0.5"
        transport=MockTransport(PLAN,{"models":price})
        with self.assertRaises(PilotStopped):
            run(transport,PLAN,"mock")
        self.assertEqual(len([x for x in transport.calls if x[0]=="/chat/completions"]),0)

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
