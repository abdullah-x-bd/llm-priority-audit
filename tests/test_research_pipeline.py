"""End-to-end research ingestion, identification, null and failure tests.

All main datasets below are SYNTHETIC. Never interpret them as model findings.
"""
import copy
import datetime as dt
import json
import random
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))

from expand_design import build_manifest
from research_pipeline import (
    FIELDS,ROSTER,IntegrityError,get_manifest,normalize_compatibility,
    validate_row,trial_schema_check,validate_collection,estimate_confirmatory,
    EQUIVALENCE_MARGIN,
)

def make_row(t,model,choice="N"):
    label=(t["q_label"] if choice=="Q" else t["n_label"]
           if choice=="N" else "")
    status="valid_Q" if choice=="Q" else "valid_N" if choice=="N" else "invalid_format"
    result={
        "trial_id":t["trial_id"],"family_id":t["family_id"],"domain":t["domain"],
        "frame":t["frame"],"condition":t["condition"],"directive":t["directive"],
        "layout":t["layout"],"mechanism":t["mechanism"],
        "pairing":t["pairing"],"q_label":t["q_label"],"n_label":t["n_label"],
        "authorized_label":t["authorized_label"],"model_id":model,
        "provider_route":"test/mock","timestamp_utc":"2026-10-10T10:00:00+00:00",
        "request_sha256":t["request_sha256"],
        "settings_json":'{"mock":true}',
        "attempt_status":status,"raw_response":label,
        "input_tokens":100,"output_tokens":1,"reasoning_tokens":0,
        "billed_cost_usd":0.0,"notes":"SYNTHETIC_TEST_NOT_EMPIRICAL",
    }
    return result

def synthetic_main(frame_priority_q=.15,frame_neutral_q=.15,seed=100):
    rng=random.Random(seed)
    result=[]
    for model in ROSTER:
        for t in build_manifest("main"):
            if t["condition"]=="zero" and t["directive"]=="N":
                p=frame_priority_q if t["frame"]=="priority" else frame_neutral_q
                choice="Q" if rng.random()<p else "N"
            else:
                choice="N"
            result.append(make_row(t,model,choice))
    return result

def compatibility_report():
    examples=[]
    for model,t in zip(ROSTER,[t for t in build_manifest("pilot")][:5]):
        label=t["n_label"]
        examples.append({
            "trial_id":t["trial_id"],"model":model,
            "request_sha256":t["request_sha256"],
            "family_id":t["family_id"],"authorized_label":t["authorized_label"],
            "returned_model":model,"status":"valid_N","output_valid":True,
            "raw_output":label,"choice":label,
            "prompt_tokens":240,"completion_tokens":2,"reasoning_tokens":0,
            "cost_usd":0.0001,"completed_utc":"2026-10-10T10:00:00+00:00"
        })
    return {"stage":"stage1","mode":"live","attempted":5,"completed":5,
            "reported_cost_usd":0.0005,"records":examples}

class IngestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=get_manifest("pilot")
        cls.model=ROSTER[0]
        cls.trial=next(iter(cls.manifest.values()))

    def test_source_report_normalizes_every_schema_field(self):
        norm=normalize_compatibility(compatibility_report())
        self.assertEqual(len(norm),5)
        for x in norm:
            self.assertEqual(set(x),FIELDS)
            self.assertEqual(x["provider_route"],None)
            self.assertEqual(x["settings_json"],None)
            self.assertTrue(trial_schema_check(x))
            self.assertEqual(x["attempt_status"],"valid_N")
        check=validate_collection(norm,"pilot")
        self.assertEqual(check["received"],5)
        self.assertEqual(check["missing_rows"],715)
        self.assertFalse(check["complete"])

    def test_mismatched_request_hash_is_rejected(self):
        data=compatibility_report()
        data["records"][0]["request_sha256"]="0"*64
        with self.assertRaisesRegex(IntegrityError,"HASH_MISMATCH"):
            normalize_compatibility(data)

    def test_wrong_action_mapping_is_rejected(self):
        data=compatibility_report()
        data["records"][0]["authorized_label"]="Z"
        with self.assertRaisesRegex(IntegrityError,"OPERATOR_LABEL_MISMATCH"):
            normalize_compatibility(data)

    def test_source_billing_mismatch_is_rejected(self):
        data=compatibility_report()
        data["reported_cost_usd"]=0.05
        with self.assertRaisesRegex(IntegrityError,"COST_TOTAL_MISMATCH"):
            normalize_compatibility(data)

    def test_duplicate_record_is_rejected(self):
        data=compatibility_report()
        data["records"].append(copy.deepcopy(data["records"][0]))
        data["attempted"]=6
        with self.assertRaisesRegex(IntegrityError,"DUPLICATE_MODEL_TRIAL"):
            normalize_compatibility(data)

    def test_bad_status_fails(self):
        t=self.trial
        x=make_row(t,self.model)
        x["attempt_status"]="valid_Q"
        with self.assertRaisesRegex(IntegrityError,"CHOICE_STATUS_INCONSISTENT"):
            validate_row(x,"pilot",self.manifest)

    def test_transport_and_invalid_model_output_differ(self):
        data=compatibility_report()
        data["records"][0]={
            "trial_id":data["records"][0]["trial_id"],
            "model":data["records"][0]["model"],
            "request_sha256":data["records"][0]["request_sha256"],
            "error":"NETWORK_UNCERTAIN"
        }
        data["completed"]=4
        data["reported_cost_usd"]=0.0004
        normalized=normalize_compatibility(data)
        self.assertEqual(normalized[0]["attempt_status"],"transport_failure")
        self.assertIsNone(normalized[0]["billed_cost_usd"])

    def test_missing_field_or_negative_cost_rejected(self):
        row=make_row(self.trial,self.model)
        del row["model_id"]
        with self.assertRaisesRegex(IntegrityError,"SCHEMA_FIELDS_MISMATCH"):
            trial_schema_check(row)
        row=make_row(self.trial,self.model)
        row["billed_cost_usd"]=-2
        with self.assertRaisesRegex(IntegrityError,"INVALID_BILLED_COST"):
            trial_schema_check(row)

class ConfirmatoryAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.null=synthetic_main(.15,.15,seed=138)
        cls.pos=synthetic_main(.40,.05,seed=138)
        cls.neg=synthetic_main(.05,.40,seed=138)

    def test_full_main_manifest_complete(self):
        v=validate_collection(self.null,"main")
        self.assertEqual(v["received"],7200)
        self.assertEqual(v["missing_rows"],0)
        self.assertTrue(v["complete"])

    def test_large_positive_effect_is_detected(self):
        r=estimate_confirmatory(self.pos)
        self.assertEqual(r["classification"],"POSITIVE_SEMANTIC_FRAME_EFFECT")
        self.assertGreater(r["estimate"],.20)
        self.assertEqual(r["primary_paired_observations"],600)
        self.assertEqual(r["primary_clusters"],15)

    def test_large_negative_effect_is_detected(self):
        r=estimate_confirmatory(self.neg)
        self.assertEqual(r["classification"],"NEGATIVE_SEMANTIC_FRAME_EFFECT")
        self.assertLess(r["estimate"],-.20)

    def test_small_null_can_be_bounded_not_proven_absent(self):
        r=estimate_confirmatory(self.null)
        self.assertIn(r["classification"],("BOUNDED_WITHIN_PREDECLARED_10PP_MARGIN",
                        "INCONCLUSIVE"))
        self.assertIsNotNone(r["confidence_interval_95pct_assumption_conditional"])
        self.assertIn("No internal model desire",r["scientific_claim"])

    def test_all_operator_compliance_is_not_false_perfect_certainty(self):
        compliant=[r.copy() for r in self.null]
        for r in compliant:
            if r["condition"]=="zero" and r["directive"]=="N":
                r["attempt_status"]="valid_N"
                t=get_manifest("main")[r["trial_id"]]
                r["raw_response"]=t["n_label"]
        stat=estimate_confirmatory(compliant)
        self.assertEqual(stat["classification"],"DEGENERATE_VARIANCE_NO_VALID_INTERVAL")
        self.assertIsNone(stat["confidence_interval_95pct_assumption_conditional"])

    def test_missing_main_cell_blocks_inference(self):
        partial=self.pos[:-1]
        r=estimate_confirmatory(partial)
        self.assertEqual(r["classification"],"INCOMPLETE_NO_CONFIRMATORY_TEST")
        self.assertEqual(r["collection"]["missing_rows"],1)

    def test_provider_error_blocks_inference(self):
        partial=[x.copy() for x in self.pos]
        partial[0]["attempt_status"]="provider_error"
        partial[0]["raw_response"]=None
        partial[0]["billed_cost_usd"]=None
        r=estimate_confirmatory(partial)
        self.assertEqual(r["classification"],"INCOMPLETE_NO_CONFIRMATORY_TEST")

    def test_invalid_model_completion_is_preserved(self):
        data=[x.copy() for x in self.pos]
        data[0]["attempt_status"]="invalid_format"
        data[0]["raw_response"]="I choose A"
        r=estimate_confirmatory(data)
        self.assertEqual(r["invalid_response_count"],1)
        self.assertTrue(r["collection"]["complete"])

    def test_route_or_settings_missing_blocks_confirmatory_inference(self):
        bad=[r.copy() for r in self.pos]
        bad[0]["provider_route"]=None
        self.assertEqual(
            estimate_confirmatory(bad)["classification"],
            "MISSING_PROVENANCE_NO_CONFIRMATORY_TEST"
        )
        bad[0]["provider_route"]="test/mock"
        bad[1]["settings_json"]=None
        self.assertEqual(
            estimate_confirmatory(bad)["classification"],
            "MISSING_PROVENANCE_NO_CONFIRMATORY_TEST"
        )

    def test_direction_and_practical_magnitude_are_separate(self):
        result=estimate_confirmatory(self.pos)
        self.assertEqual(result["statistical_direction"],"POSITIVE")
        self.assertIn(result["practical_magnitude"],
                      ("AT_LEAST_10PP_POSITIVE","UNRESOLVED",
                       "BOUNDED_WITHIN_PLUS_MINUS_10PP"))
        self.assertEqual(result["invalid_preference_worst_case_bounds"][0],
                         result["invalid_preference_worst_case_bounds"][1])

    def test_invalid_choice_sensitivity_is_reported(self):
        corrupt=[r.copy() for r in self.pos]
        matched=[r for r in corrupt if
                 r["condition"]=="zero" and r["directive"]=="N" and
                 r["frame"]=="priority"][:10]
        for r in matched:
            r["attempt_status"]="invalid_format"
            r["raw_response"]="A or B"
        result=estimate_confirmatory(corrupt)
        self.assertEqual(result["invalid_response_count"],10)
        low,high=result["invalid_preference_worst_case_bounds"]
        self.assertLess(low,high)
        self.assertEqual(result["primary_clusters"],15)

    def test_pilot_rows_cannot_be_analyzed_as_main(self):
        pilot=normalize_compatibility(compatibility_report())
        with self.assertRaisesRegex(IntegrityError,"UNKNOWN_TRIAL_ID"):
            validate_collection(pilot,"main")

if __name__=="__main__":
    unittest.main()
