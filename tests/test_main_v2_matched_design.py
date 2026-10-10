"""V2 main has matched actions, balanced layouts, and immutable v1 source."""
import json,sys,unittest
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from main_v2_matched_design import PATTERNS,source_families,main_v2_manifest,COMMON_NOTES
from expand_design import load_families

class MainV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.families=source_families()
        cls.trials=main_v2_manifest()
    def test_size_and_mechanism_distinction(self):
        self.assertEqual(len(self.families),60)
        self.assertEqual(len(PATTERNS),15)
        self.assertEqual(Counter(f["mechanism"] for f in self.families),{x:4 for x in PATTERNS})
        self.assertEqual(len(self.trials),1440)
        self.assertEqual(len({x["trial_id"] for x in self.trials}),1440)
    def test_mechanism_unique_pair_not_universal_template(self):
        for domain in ("continuation","reversibility","verification"):
            mechanisms={f["mechanism"] for f in self.families if f["domain"]==domain}
            self.assertEqual(len(mechanisms),5)
            pairings={(PATTERNS[m]["Q"],PATTERNS[m]["N"]) for m in mechanisms}
            self.assertEqual(len(pairings),5)
        for fam in self.families:
            self.assertNotIn("configuration K17",fam["neutral_action_q"])
            self.assertNotIn("preset",fam["neutral_action_n"].lower())
            self.assertEqual(fam["operator_authority"],"")
            self.assertIn(COMMON_NOTES[fam["domain"]],fam["context"])
    def test_framing_variants_roughly_equal_length(self):
        for mechanism, wording in PATTERNS.items():
            for a,b in (("Q","q"),("N","n")):
                with self.subTest(mechanism=mechanism,option=a):
                    ratio=len(wording[a])/len(wording[b])
                    self.assertGreaterEqual(ratio,.80)
                    self.assertLessEqual(ratio,1.25)

    def test_v1_source_unchanged(self):
        old={x["family_id"]:x for x in load_families("main")}
        self.assertEqual(set(old),{x["family_id"] for x in self.families})
        for f in self.families:
            self.assertEqual(f["outcomes"],old[f["family_id"]]["outcomes"])
            self.assertNotEqual(f["action_q"],old[f["family_id"]]["action_q"])
            self.assertNotEqual(f["neutral_action_q"],old[f["family_id"]]["neutral_action_q"])
    def test_one_operator_directive_and_full_factorial(self):
        for f in self.families:
            r=[x for x in self.trials if x["family_id"]==f["family_id"]]
            self.assertEqual(len(r),24)
            self.assertEqual(set(x["frame"] for x in r),{"neutral","priority"})
            self.assertEqual(set(x["condition"] for x in r),{"positive","zero","negative"})
            self.assertEqual(set(x["directive"] for x in r),{"N","Q"})
            self.assertEqual(set(x["layout"] for x in r),{"layout0","layout1"})
            for trial in r:
                self.assertEqual(trial["user_message"].count("Operator directive:"),1)
                self.assertNotIn("This operator has final authority",trial["user_message"])
                self.assertNotIn("The directive is deliberate",trial["user_message"])
                self.assertNotIn("approved configuration K17",trial["user_message"])
                self.assertEqual(trial["phase"],"main_v2_candidate")
                self.assertEqual(trial["v2_review_status"],"NOT_INDEPENDENTLY_APPROVED")
    def test_matched_material_action_across_frames(self):
        for f in self.families:
            r=[x for x in self.trials if x["family_id"]==f["family_id"] and
               x["condition"]=="zero" and x["directive"]=="N" and x["layout"]=="layout0"]
            self.assertEqual(len(r),2)
            a,b=sorted(r,key=lambda x:x["frame"])
            self.assertEqual(a["authorized_label"],b["authorized_label"])
            self.assertEqual(a["q_label"],b["q_label"])
            self.assertEqual(a["n_label"],b["n_label"])
            self.assertEqual(a["system_message"],b["system_message"])
            self.assertNotEqual(a["request_sha256"],b["request_sha256"])
    def test_duplicate_contexts_are_not_created_by_mechanism_expansion(self):
        for mechanism in PATTERNS:
            contexts={x["context"] for x in self.families if x["mechanism"]==mechanism}
            self.assertEqual(len(contexts),4)
if __name__=="__main__":unittest.main()
