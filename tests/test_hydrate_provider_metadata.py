"""GET-only metadata hydration preserves pilot observations."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from hydrate_provider_metadata import hydrate,gen_id
class NonBillingTransport:
    def __init__(self):self.paths=[]
    def request(self,path,body=None):
        self.paths.append((path,body))
        if not path.startswith("/generation?id=") or body is not None:
            raise RuntimeError("Disallowed model inference request")
        return {"data":{"provider_name":"DeepInfra","model":"deepseek/deepseek-v3.2-20251201","total_cost":0.0001}}
class HydrationTests(unittest.TestCase):
    def test_get_only_resolution(self):
        source={"notes":"PILOT ONLY; generation_id=gen-test-123; provider_metadata_error=HTTP_404",
                "provider_route":None,"billed_cost_usd":0.0001}
        mock=NonBillingTransport()
        hydrated,issues=hydrate([source],mock,wait=0)
        self.assertEqual(hydrated[0]["provider_route"],"DeepInfra")
        self.assertEqual(len(issues),0)
        self.assertEqual(source["provider_route"],None)
        self.assertEqual(len(mock.paths),1)
        self.assertIsNone(mock.paths[0][1])
    def test_missing_id_keeps_record_without_invention(self):
        mock=NonBillingTransport()
        rows,issues=hydrate([{"notes":"no id","provider_route":None}],mock,wait=0)
        self.assertIsNone(rows[0]["provider_route"])
        self.assertEqual(issues[0]["reason"],"MISSING_GENERATION_ID")
if __name__=="__main__": unittest.main()
