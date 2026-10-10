"""One concise AI-model review per source, no duplicate requests, no expensive extras."""
import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from claude_one_pass_review import Mock,run,cases,prompt,reserve,CAP,MODEL

class ReviewTests(unittest.TestCase):
    def test_66_sources_without_experimental_outcomes(self):
        c=cases()
        self.assertEqual(len(c),66)
        self.assertEqual({p for p,_ in c},{"main","new_calibration"})
        self.assertEqual(len({f["family_id"] for p,f in c}),66)
        for phase,f in c:
            p=prompt(f)
            self.assertIn("Version X:",p)
            self.assertIn("Version Y:",p)
            self.assertNotIn("pilot revealed",p)
            self.assertNotIn("model responses showed",p)
            self.assertLess(reserve(p)*66,CAP)
    def test_complete_mock_one_request_per_family(self):
        with tempfile.TemporaryDirectory() as tmp:
            service=Mock();path=Path(tmp)/"results.json"
            r=run(service,limit=66,path=path)
            self.assertEqual(r["status"],"finished")
            self.assertEqual(service.count,66)
            self.assertEqual(len(r["results"]),66)
            self.assertEqual(sum(bool(x["opinion"]) for x in r["results"]),66)
            self.assertLessEqual(r["known_usd"]+r["unknown_reserved_usd"],CAP)
            r2=run(service,limit=66,path=path)
            self.assertEqual(service.count,66)
            self.assertEqual(len(r2["results"]),66)
    def test_mock_partial_resume_no_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            service=Mock();path=Path(tmp)/"results.json"
            first=run(service,limit=6,path=path)
            self.assertEqual(len(first["results"]),6)
            final=run(service,limit=12,path=path)
            self.assertEqual(len(final["results"]),12)
            self.assertEqual(service.count,12)
    def test_pending_record_blocks_automatic_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"results.json"
            first=run(Mock(),limit=1,path=path)
            first["inflight"]={"index":1,"family_id":"UNKNOWN","reserved_usd":.02}
            path.write_text(json.dumps(first),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"UNCERTAIN_PRIOR_PAID_ATTEMPT"):
                run(Mock(),limit=3,path=path)

if __name__=="__main__": unittest.main()
