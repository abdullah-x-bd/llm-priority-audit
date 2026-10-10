"""No-network acceptance and failure-injection for the full 720-call pilot."""
import json
import os
from unittest import mock
import tempfile
import unittest
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from full_pilot import (FakeService, collect, sample_plan, check_authorization,
                        STAGE1_COST, BUDGET, SAMPLE_COUNT)
from pilot_compatibility import APIProblem, PilotStopped

REF=json.loads((Path(__file__).resolve().parents[1]/"config"/"pricing-assumptions.json").read_text())

class FakeFailsAfter(FakeService):
    def __init__(self,ref,n):
        super().__init__(ref)
        self.fail_at=n
    def request(self,path,body=None):
        if path=="/chat/completions" and self.calls>=self.fail_at:
            raise APIProblem("NETWORK_UNCERTAIN")
        return super().request(path,body)

class FakeExpensive(FakeService):
    def request(self,path,body=None):
        x=super().request(path,body)
        if path=="/chat/completions":
            x["usage"]["cost"]=0.02
        return x

class CollectorTests(unittest.TestCase):
    def test_authorization_matches_protocol(self):
        check_authorization()
        ref,ordered=sample_plan()
        self.assertEqual(len(ordered),720)
        self.assertEqual(len(set((m,t["trial_id"]) for m,t in ordered)),720)
        c=Counter(m for m,t in ordered)
        self.assertEqual(set(c.values()),{144})
        for m in c:
            models=[t for x,t in ordered if x==m]
            self.assertEqual(Counter(t["frame"] for t in models),
                             {"priority":72,"neutral":72})
            self.assertEqual(Counter(t["condition"] for t in models),
                             {"positive":48,"zero":48,"negative":48})
            self.assertEqual(Counter(t["directive"] for t in models),
                             {"Q":72,"N":72})

    def test_full_mock_720_ingestion_and_resume_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            transport=FakeService(REF)
            result=collect(transport,out,"mock")
            self.assertEqual(result["status"],"finished")
            self.assertEqual(len(result["collected"]),720)
            self.assertEqual(transport.calls,720)
            self.assertLess(STAGE1_COST+result["cost_usd"],BUDGET)
            report=json.loads((out/"full-pilot-mock-report.json").read_text())
            self.assertEqual(report["canonical_validation"]["missing_rows"],0)
            self.assertEqual(report["canonical_validation"]["expected"],720)
            self.assertEqual(report["unresolved_provider_routes"],0)
            self.assertEqual(len(report["models"]),5)
            assert all(x["status"] in ("valid_N","valid_Q") for x in []) # no-op
            # A second invocation must not spend money or recreate responses.
            second=FakeService(REF)
            again=collect(second,out,"mock")
            self.assertEqual(again["status"],"finished")
            self.assertEqual(second.calls,0)
            self.assertEqual(len(again["collected"]),720)

    def test_injected_network_failure_does_not_retry_uncertain_charge(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            m=FakeFailsAfter(REF,3)
            checkpoint=collect(m,out,"mock")
            self.assertEqual(len(checkpoint["collected"]),3)
            self.assertIn("STOP_UNCERTAIN_CHARGE",checkpoint["status"])
            self.assertIsNotNone(checkpoint["inflight"])
            again=FakeService(REF)
            with self.assertRaisesRegex(PilotStopped,"UNCERTAIN_PRIOR_INFLIGHT"):
                collect(again,out,"mock")
            self.assertEqual(again.calls,0)

    def test_reservation_limit_stops_before_overspend(self):
        with tempfile.TemporaryDirectory() as temp:
            state=collect(FakeExpensive(REF),Path(temp),"mock")
            self.assertLessEqual(state["cost_usd"]+STAGE1_COST,BUDGET)
            self.assertEqual(state["status"],"STOP_BUDGET_RESERVATION")
            self.assertLess(len(state["collected"]),720)

    def test_short_explicit_mode_can_be_resumed_without_duplicate_calls(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            first=FakeService(REF)
            a=collect(first,out,"mock",max_requests=5)
            self.assertEqual(a["status"],"PARTIAL_EXPLICIT_TEST")
            self.assertEqual(len(a["collected"]),5)
            second=FakeService(REF)
            b=collect(second,out,"mock",max_requests=9)
            self.assertEqual(len(b["collected"]),9)
            self.assertEqual(second.calls,4)
            self.assertEqual(len(set((r["model_id"],r["trial_id"]) for r in b["collected"])),9)

    def test_manual_http400_recovery_requires_explicit_acknowledgement(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            first=FakeFailsAfter(REF,0)
            first.fail_at=0
            # The mock raises an HTTP400 before any model generation occurs.
            class BadParameter(FakeService):
                def request(self,path,body=None):
                    if path=="/chat/completions":
                        raise APIProblem("HTTP_400_invalid_request")
                    return super().request(path,body)
            state=collect(BadParameter(REF),out,"mock")
            self.assertEqual(len(state["collected"]),0)
            self.assertTrue(state["status"].startswith("STOP_UNCERTAIN_CHARGE_HTTP_400"))
            with self.assertRaisesRegex(PilotStopped,"UNCERTAIN_PRIOR_INFLIGHT"):
                collect(FakeService(REF),out,"mock",max_requests=5)
            with mock.patch.dict(os.environ,
                  {"FULL_PILOT_RECOVER_HTTP400":"ACKNOWLEDGED_INVALID_REQUEST"}):
                fixed=collect(FakeService(REF),out,"mock",max_requests=5)
            self.assertEqual(len(fixed["collected"]),5)
            self.assertEqual(len(fixed["rejected_attempts"]),1)

    def test_never_touch_main_source(self):
        _,selected=sample_plan()
        self.assertTrue(all(int(t["family_id"].split("-")[-1])>=91 for _,t in selected))

if __name__=="__main__":
    unittest.main()
