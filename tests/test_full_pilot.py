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

    def test_rate_limit_is_not_silently_replayed_and_resume_retains_earlier_records(self):
        class RateLimited(FakeService):
            def request(self,path,body=None):
                if path=="/chat/completions" and self.calls>=3:
                    raise APIProblem("HTTP_429_rate_limit_exceeded")
                return super().request(path,body)
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            first=collect(RateLimited(REF),out,"mock")
            self.assertEqual(len(first["collected"]),3)
            self.assertIn("STOP_UNCERTAIN_CHARGE_HTTP_429",first["status"])
            with self.assertRaisesRegex(PilotStopped,"UNCERTAIN_PRIOR_INFLIGHT"):
                collect(FakeService(REF),out,"mock",max_requests=6)
            with mock.patch.dict(os.environ,{"FULL_PILOT_RECOVER_HTTP429":"ACKNOWLEDGED_RATE_LIMIT"}):
                final=collect(FakeService(REF),out,"mock",max_requests=6)
            self.assertEqual(len(final["collected"]),6)
            self.assertEqual(len(final["rejected_attempts"]),1)
            self.assertEqual(len(set((x["model_id"],x["trial_id"]) for x in final["collected"])),6)

    def test_nonzero_http400_recovery_reserves_unknown_cost(self):
        class RejectAfterThree(FakeService):
            def request(self,path,body=None):
                if path=="/chat/completions" and self.calls>=3:
                    raise APIProblem("HTTP_400__Provider returned error")
                return super().request(path,body)
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            first=collect(RejectAfterThree(REF),out,"mock")
            self.assertEqual(len(first["collected"]),3)
            with self.assertRaisesRegex(PilotStopped,"UNCERTAIN_PRIOR_INFLIGHT"):
                collect(FakeService(REF),out,"mock",max_requests=7)
            with mock.patch.dict(os.environ,
                      {"FULL_PILOT_RECOVER_HTTP400":"ACKNOWLEDGED_INVALID_REQUEST"}):
                recovered=collect(FakeService(REF),out,"mock",max_requests=7)
            self.assertEqual(len(recovered["collected"]),7)
            self.assertEqual(len(recovered["rejected_attempts"]),1)
            report=json.loads((out/"full-pilot-mock-report.json").read_text())
            self.assertGreaterEqual(report["unresolved_rejection_reserve_usd"],0.03)
            self.assertLessEqual(
                report["all_pilot_reported_cost_usd"]+
                report["unresolved_rejection_reserve_usd"],BUDGET)

    def test_deepseek_provider_has_one_verified_no_fallback_route(self):
        from full_pilot import DEEPSEEK_PILOT_PROVIDERS
        self.assertEqual(DEEPSEEK_PILOT_PROVIDERS,["AtlasCloud"])

    def test_mismatched_model_is_preserved_and_verified_probe_replaces_one_trial(self):
        _,plan=sample_plan()
        index=next(i for i,(model,trial) in enumerate(plan)
                   if model=="deepseek/deepseek-v3.2" and i>=3)
        expected_model,trial=plan[index]
        class MismatchedModel(FakeService):
            def request(self,path,body=None):
                result=super().request(path,body)
                if path=="/chat/completions" and self.calls==index+1:
                    result["model"]="another/unapproved-model"
                return result
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            first=collect(MismatchedModel(REF),root,"mock")
            self.assertEqual(len(first["collected"]),index)
            self.assertIn("MODEL_RETURNED_DIFFERENT_IDENTIFIER",first["status"])
            self.assertEqual(first["unaccepted_response"]["returned_model"],
                             "another/unapproved-model")
            probe={
                "trial_id":trial["trial_id"],"request_sha256":trial["request_sha256"],
                "requested_model":expected_model,"returned_model":expected_model,
                "provider_expected":"AtlasCloud","completion_id":"mock-verified-probe",
                "content":trial["authorized_label"],
                "usage":{"cost":0.00012,"prompt_tokens":220,"completion_tokens":1,
                         "completion_tokens_details":{"reasoning_tokens":0}},
                "settings":{"model":expected_model,"max_tokens":64,
                            "provider":{"only":["AtlasCloud"],"allow_fallbacks":False}},
            }
            path=root/"one-probe.json"
            path.write_text(json.dumps(probe),encoding="utf-8")
            with self.assertRaisesRegex(PilotStopped,"UNCERTAIN_PRIOR_INFLIGHT"):
                collect(FakeService(REF),root,"mock",max_requests=index+2)
            with mock.patch.dict(os.environ,{"FULL_PILOT_RECONCILE_PROBE":str(path)}):
                recovered=collect(FakeService(REF),root,"mock",max_requests=index+2)
            self.assertEqual(len(recovered["collected"]),index+2)
            self.assertEqual(recovered["probe_run_id"],38048702034)
            self.assertEqual(recovered["collected"][index]["model_id"],expected_model)
            self.assertEqual(recovered["collected"][index]["trial_id"],trial["trial_id"])
            self.assertEqual(len(recovered["rejected_attempts"]),1)
            self.assertEqual(len(set((r["model_id"],r["trial_id"])
                                 for r in recovered["collected"])),index+2)

    def test_live_success_skips_global_sleep_and_deferred_generation_lookup(self):
        class CountRoutes(FakeService):
            def __init__(self,plan):
                super().__init__(plan)
                self.generation_calls=0
            def request(self,path,body=None):
                if path.startswith("/generation?"):
                    self.generation_calls+=1
                return super().request(path,body)
        with tempfile.TemporaryDirectory() as temp:
            transport=CountRoutes(REF)
            with mock.patch("full_pilot.time.sleep") as sleep:
                state=collect(transport,Path(temp),"live",max_requests=8)
            self.assertEqual(len(state["collected"]),8)
            self.assertEqual(transport.generation_calls,0)
            sleep.assert_not_called()
            self.assertTrue(all(r["provider_route"] is None for r in state["collected"]))

    def test_live_http429_bounded_retry_preserves_rejected_liability(self):
        class RateLimitOnce(FakeService):
            def __init__(self,plan):
                super().__init__(plan)
                self.rejected=0
            def request(self,path,body=None):
                if path=="/chat/completions" and self.calls==3 and self.rejected==0:
                    self.rejected+=1
                    raise APIProblem("HTTP_429_rate_limit_exceeded",http_status=429,retry_after=45)
                return super().request(path,body)
        with tempfile.TemporaryDirectory() as temp:
            transport=RateLimitOnce(REF)
            with mock.patch("full_pilot.time.sleep") as sleep:
                result=collect(transport,Path(temp),"live",max_requests=7)
            self.assertEqual(result["status"],"PARTIAL_EXPLICIT_TEST")
            self.assertEqual(len(result["collected"]),7)
            self.assertEqual(transport.rejected,1)
            self.assertEqual(len(result["rejected_attempts"]),1)
            self.assertGreaterEqual(result["unresolved_rejection_reserve_usd"],0.03)
            sleep.assert_called_once_with(45)

    def test_live_network_uncertainty_is_never_retried(self):
        class NetworkError(FakeService):
            def __init__(self,ref):
                super().__init__(ref)
                self.failed_calls=0
            def request(self,path,body=None):
                if path=="/chat/completions":
                    self.failed_calls+=1
                    raise APIProblem("NETWORK_UNCERTAIN")
                return super().request(path,body)
        with tempfile.TemporaryDirectory() as temp:
            transport=NetworkError(REF)
            with mock.patch("full_pilot.time.sleep") as sleep:
                result=collect(transport,Path(temp),"live")
            self.assertEqual(result["status"],"STOP_UNCERTAIN_CHARGE_NETWORK_UNCERTAIN")
            self.assertEqual(len(result["collected"]),0)
            self.assertEqual(transport.failed_calls,1)
            sleep.assert_not_called()

    def test_raw_first_archives_incomplete_http200_and_continues(self):
        class IncompleteOnce(FakeService):
            def request(self,path,body=None):
                response=super().request(path,body)
                if path=="/chat/completions" and self.calls==4:
                    return {"id":"gen-incomplete-mock","error":{"code":502,
                            "message":"upstream provider failed"}}
                return response
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ,{"FULL_PILOT_RAW_FIRST":"1"}):
                with mock.patch("full_pilot.time.sleep"):
                    state=collect(IncompleteOnce(REF),Path(tmp),"live",max_requests=8)
            self.assertEqual(state["status"],"PARTIAL_EXPLICIT_TEST")
            self.assertEqual(len(state["collected"]),8)
            self.assertEqual(state["collected"][3]["attempt_status"],"provider_error")
            self.assertIsNone(state["collected"][3]["billed_cost_usd"])
            self.assertEqual(len(state["raw_events"]),8)
            self.assertEqual(state["raw_events"][3]["response"]["id"],"gen-incomplete-mock")
            self.assertEqual(state["raw_events"][3]["response"]["error"]["code"],502)
            self.assertGreaterEqual(state["unresolved_rejection_reserve_usd"],.03)
            self.assertEqual(state["collected"][4]["attempt_status"],"valid_N"
                             if state["collected"][4]["directive"]=="N" else "valid_Q")

    def test_raw_first_preserves_mismatched_model_without_validating_as_choice(self):
        class WrongModel(FakeService):
            def request(self,path,body=None):
                response=super().request(path,body)
                if path=="/chat/completions" and self.calls==2:
                    response["model"]="another/unapproved-model"
                return response
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ,{"FULL_PILOT_RAW_FIRST":"1"}):
                with mock.patch("full_pilot.time.sleep"):
                    result=collect(WrongModel(REF),Path(tmp),"live",max_requests=5)
            self.assertEqual(len(result["collected"]),5)
            self.assertEqual(result["collected"][1]["attempt_status"],"provider_error")
            self.assertEqual(result["collected"][1]["billed_cost_usd"],.00012)
            self.assertEqual(result["raw_events"][1]["response"]["model"],"another/unapproved-model")
            self.assertIsNone(result["inflight"])

    def test_raw_first_network_failure_is_not_a_choice_and_never_retried(self):
        class FailsOnce(FakeService):
            def __init__(self,ref):
                super().__init__(ref)
                self.failed=False
            def request(self,path,body=None):
                if path=="/chat/completions" and self.calls==1 and not self.failed:
                    self.failed=True
                    raise APIProblem("NETWORK_UNCERTAIN")
                return super().request(path,body)
        with tempfile.TemporaryDirectory() as tmp:
            service=FailsOnce(REF)
            with mock.patch.dict(os.environ,{"FULL_PILOT_RAW_FIRST":"1"}):
                with mock.patch("full_pilot.time.sleep"):
                    result=collect(service,Path(tmp),"live",max_requests=5)
            self.assertEqual(len(result["collected"]),5)
            self.assertEqual(service.calls,4)
            self.assertEqual(result["collected"][1]["attempt_status"],"transport_failure")
            self.assertEqual(result["raw_events"][1]["error"]["reason"],"NETWORK_UNCERTAIN")
            self.assertEqual(sum(r["attempt_status"]=="transport_failure"
                                 for r in result["collected"]),1)

    def test_raw_first_entire_partial_batch_allows_incomplete_pilot_rows(self):
        class ProviderFailure(FakeService):
            def request(self,path,body=None):
                response=super().request(path,body)
                if path=="/chat/completions" and self.calls==8:
                    return {"id":"gen-error","error":{"code":502},"usage":{"cost":.00012}}
                return response
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ,{"FULL_PILOT_RAW_FIRST":"1"}):
                with mock.patch("full_pilot.time.sleep"):
                    result=collect(ProviderFailure(REF),Path(tmp),"live",max_requests=9)
            self.assertEqual(len(result["collected"]),9)
            self.assertEqual(result["collected"][7]["attempt_status"],"provider_error")
            self.assertEqual(result["raw_events"][7]["response"]["id"],"gen-error")
            self.assertEqual(result["collected"][7]["billed_cost_usd"],.00012)
            self.assertEqual(len({(r["model_id"],r["trial_id"]) for r in result["collected"]}),9)

    def test_raw_first_can_finish_720_attempts_with_a_provider_failure(self):
        class OneIncompleteEnvelope(FakeService):
            def request(self,path,body=None):
                response=super().request(path,body)
                if path=="/chat/completions" and self.calls==123:
                    return {"id":"gen-synthetic123","error":{"code":502}}
                return response
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ,{"FULL_PILOT_RAW_FIRST":"1"}):
                with mock.patch("full_pilot.time.sleep"):
                    result=collect(OneIncompleteEnvelope(REF),Path(tmp),"live")
            self.assertEqual(len(result["collected"]),720)
            self.assertEqual(result["status"],"finished_with_unresolved_responses")
            self.assertEqual(len(result["raw_events"]),720)
            self.assertEqual(result["collected"][122]["attempt_status"],"provider_error")
            r=json.loads((Path(tmp)/"full-pilot-live-report.json").read_text())
            self.assertEqual(r["raw_capture_event_count"],720)
            self.assertEqual(r["unresolved_response_count"],1)
            self.assertFalse(r["canonical_validation"]["complete"])
            self.assertGreater(r["unresolved_rejection_reserve_usd"],0)


    def test_recover_legacy_http200_missing_model_without_retry(self):
        class LegacyIncomplete(FakeService):
            def request(self,path,body=None):
                response=super().request(path,body)
                if path=="/chat/completions" and self.calls==4:
                    return {"id":"gen-original-legacy-missing-model"}
                return response
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)
            with mock.patch("full_pilot.time.sleep"):
                previous=collect(LegacyIncomplete(REF),out,"live")
            self.assertEqual(len(previous["collected"]),3)
            self.assertEqual(previous["inflight"]["index"],3)
            self.assertIsNone(previous["unaccepted_response"]["returned_model"])
            # Earlier production runs used the less precise legacy error name.
            checkpoint=out/"full-pilot-live-checkpoint.json"
            legacy=json.loads(checkpoint.read_text())
            legacy["status"]="STOP_UNINTERPRETABLE_BILLING_OR_MODEL_MODEL_RETURNED_DIFFERENT_IDENTIFIER"
            checkpoint.write_text(json.dumps(legacy),encoding="utf-8")
            second=FakeService(REF)
            with mock.patch.dict(os.environ,{
                  "FULL_PILOT_RAW_FIRST":"1",
                  "FULL_PILOT_RECOVER_LEGACY_INCOMPLETE":"ACKNOWLEDGE_AND_SKIP_UNBILLED_UNKNOWN"}):
                with mock.patch("full_pilot.time.sleep"):
                    resumed=collect(second,out,"live",max_requests=7)
            self.assertEqual(len(resumed["collected"]),7)
            self.assertEqual(second.calls,3)
            self.assertEqual(resumed["collected"][3]["attempt_status"],"provider_error")
            self.assertIsNone(resumed["collected"][3]["settings_json"])
            self.assertEqual(len(resumed["rejected_attempts"]),1)
            self.assertEqual(len(resumed["recovery_events"]),1)
            self.assertFalse(resumed["recovery_events"][0]["raw_response_available"])
            self.assertEqual(len(resumed["raw_events"]),3)
            self.assertEqual(resumed["raw_events"][0]["index"],4)

    def test_never_touch_main_source(self):
        _,selected=sample_plan()
        self.assertTrue(all(int(t["family_id"].split("-")[-1])>=91 for _,t in selected))

if __name__=="__main__":
    unittest.main()
