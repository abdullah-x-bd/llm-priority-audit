"""Raw-first capture and post-hoc analysis are deliberately separate."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from expand_design import build_manifest
from raw_capture import raw_event,classify_saved_event
from posthoc_pilot import audit_checkpoint

TRIAL=build_manifest("pilot")[0]
MODEL="deepseek/deepseek-v3.2"
PAYLOAD={"model":MODEL,"messages":[{"role":"user","content":"fictional scenario"}],
         "max_tokens":64,"provider":{"only":["AtlasCloud"],"allow_fallbacks":False}}
class OfflineClassification(unittest.TestCase):
    def test_actual_A_B_classified_from_raw_only(self):
        for v,label in [("Q",TRIAL["q_label"]),("N",TRIAL["n_label"])]:
            with self.subTest(v=v):
                envelope={"id":"gen-test","model":MODEL,
                          "choices":[{"message":{"content":label}}],
                          "usage":{"cost":0.0001}}
                ev=raw_event(0,MODEL,TRIAL,PAYLOAD,response=envelope,reservation=.03)
                classified=classify_saved_event(ev,TRIAL)
                self.assertEqual(classified["category"],"valid_"+v)
                self.assertEqual(classified["observed_letter"],label)
                self.assertNotIn("messages",ev["request_settings"])
    def test_missing_model_is_unresolved_even_if_letter_present(self):
        ev=raw_event(0,MODEL,TRIAL,PAYLOAD,response={
            "id":"gen-provider-fail","choices":[{"message":{"content":"A"}}],
            "usage":{"cost":.0002}})
        x=classify_saved_event(ev,TRIAL)
        self.assertEqual(x["category"],"missing_model_identity")
        self.assertIsNone(x["observed_letter"])
    def test_nested_and_top_level_provider_errors(self):
        for r in ({"error":{"code":502}},
                  {"model":MODEL,"choices":[{"error":{"message":"bad"},"message":{"content":"A"}}],
                   "usage":{"cost":.0001}}):
            with self.subTest(r=r):
                ev=raw_event(0,MODEL,TRIAL,PAYLOAD,response=r)
                self.assertEqual(classify_saved_event(ev,TRIAL)["category"],"provider_error")
    def test_transport_error_is_not_a_choice(self):
        ev=raw_event(0,MODEL,TRIAL,PAYLOAD,error={"type":"network_or_response_error",
                                                 "reason":"NETWORK_UNCERTAIN"})
        self.assertEqual(classify_saved_event(ev,TRIAL)["category"],"transport_failure")
    def test_posthoc_summary_discloses_missing_legacy_raw_envelopes(self):
        ev=raw_event(5,MODEL,TRIAL,PAYLOAD,response={
            "id":"gen-test","model":MODEL,
            "choices":[{"message":{"content":TRIAL["q_label"]}}],
            "usage":{"cost":.0001}})
        state={"raw_events":[ev],"collected":[{"old":True}]*6}
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"checkpoint.json"
            p.write_text(json.dumps(state),encoding="utf-8")
            result=audit_checkpoint(p)
        self.assertEqual(result["raw_events_available"],1)
        self.assertEqual(result["older_rows_without_raw_envelopes"],5)
        self.assertEqual(result["category_counts"]["valid_Q"],1)
    def test_manifest_tampering_is_rejected(self):
        ev=raw_event(0,MODEL,TRIAL,PAYLOAD,response={"model":MODEL})
        ev["request_sha256"]="tampered"
        with self.assertRaisesRegex(ValueError,"RAW_EVENT_MANIFEST_MISMATCH"):
            classify_saved_event(ev,TRIAL)

if __name__=="__main__":
    unittest.main()
