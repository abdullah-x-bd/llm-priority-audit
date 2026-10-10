"""Review gates never confuse blanks with independent approval."""
import csv,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from generate_blind_review import generate,REVIEW_CATEGORIES
from check_independent_review import audit
class ReviewGateTests(unittest.TestCase):
    def test_blank_120_reviews_are_not_signed_off(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            generate(root)
            result=audit(root/"blank-reviewer-ratings.csv")
            self.assertEqual(result["status"],"NO_GO_INDEPENDENT_REVIEW_PENDING")
            self.assertEqual(result["families_with_unresolved_reviews"],60)
            self.assertEqual(result["expected_independent_reviews"],120)
    def test_signed_rows_require_every_criterion(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);generate(root)
            p=root/"blank-reviewer-ratings.csv"
            with p.open() as f:r=list(csv.DictReader(f))
            for i,row in enumerate(r):
                row.update({"actual_reviewer_id":"external-reviewer-"+str(i%2),
                      "independent_affiliation":"verified independent institution",
                      "date_utc":"2026-11-01",
                      "reviewed_blinded_X_Y":"yes",
                      "overall_decision":"approve",
                      "reviewer_signature_or_confirmed_email":"identity-confirmed"})
                for k in REVIEW_CATEGORIES:row["rating_"+k]="pass"
            with p.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(r[0]));w.writeheader();w.writerows(r)
            valid=audit(p)
            self.assertEqual(valid["status"],"REVIEW_RECORDS_PRESENT_NEED_EXTERNAL_PROVENANCE_CHECK")
            r[0]["rating_neutral_control_lexical_valence"]="reject"
            with p.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(r[0]));w.writeheader();w.writerows(r)
            denied=audit(p)
            self.assertEqual(denied["status"],"NO_GO_INDEPENDENT_REVIEW_PENDING")
            self.assertEqual(denied["families_with_unresolved_reviews"],1)
if __name__=="__main__": unittest.main()
