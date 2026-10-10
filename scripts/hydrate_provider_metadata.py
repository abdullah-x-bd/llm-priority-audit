#!/usr/bin/env python3
"""Resolve OpenRouter generation metadata AFTER batch completion, GET-only.

Input remains unchanged. Output is a separate fully validated canonical file.
No inference requests are made; this tool only calls GET /api/v1/generation.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from pilot_compatibility import Transport, APIProblem
from research_pipeline import read_records,write_records,validate_collection

ID_RE=re.compile(r"(?:^|; )generation_id=([^;]+)")
def gen_id(record):
    match=ID_RE.search(record.get("notes",""))
    return match.group(1) if match else None

def hydrate(rows,transport,wait=0.4):
    out=[]
    issues=[]
    for i,src in enumerate(rows):
        x=src.copy()
        id=gen_id(x)
        if not id:
            issues.append({"row":i,"reason":"MISSING_GENERATION_ID"})
            out.append(x)
            continue
        from urllib.parse import quote
        meta={}
        problem=None
        for attempt in range(3):
            try:
                response=transport.request("/generation?id="+quote(id,safe=""))
                meta=response.get("data") or {}
                if not isinstance(meta,dict):
                    problem="MALFORMED_METADATA"
                    break
                if meta.get("provider_name"):
                    problem=None
                    break
                problem="PROVIDER_NAME_NOT_YET_AVAILABLE"
            except APIProblem as e:
                problem=str(e).split("_",3)[:2]
                problem="_".join(problem)
            except (ValueError,TypeError):
                problem="NONBILLABLE_METADATA_ERROR"
                break
            # The OpenRouter generation metadata API is eventually
            # consistent. GET retries cannot generate any model charges.
            if attempt<2:
                time.sleep(3*(attempt+1))
        name=meta.get("provider_name")
        if isinstance(name,str) and name:
            x["provider_route"]=name
            revision=meta.get("model")
            cost=meta.get("total_cost")
            x["notes"]+="; generation_resolved_model="+str(revision)
            if isinstance(cost,(int,float)) and cost>=0:
                x["notes"]+="; generation_resolved_cost="+str(cost)
                if x.get("billed_cost_usd") is not None and abs(cost-x["billed_cost_usd"])>0.00003:
                    issues.append({"row":i,"reason":"COST_RECONCILIATION_DIFFERENCE"})
        else:
            issues.append({"row":i,"reason":problem or "PROVIDER_NAME_ABSENT"})
        out.append(x)
        if wait>0:
            time.sleep(wait)
        if (i+1)%120==0:
            print(json.dumps({"metadata_lookup_progress":i+1,"of":len(rows),
                              "resolved":sum(v["provider_route"] is not None for v in out)}),flush=True)
    return out,issues

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--issues",required=True,type=Path)
    a=ap.parse_args()
    key=os.getenv("OPENROUTER_API_KEY","")
    if not key:raise SystemExit("Key secret missing; no charged requests performed")
    rows=read_records(a.input)
    check=validate_collection(rows,"pilot")
    if not check["complete"]:
        raise SystemExit("Full pilot is incomplete; metadata hydration must await resolution.")
    result,issues=hydrate(rows,Transport(key))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    write_records(a.output,result)
    a.issues.write_text(json.dumps({"issues":issues,"records":len(result),
        "routes_resolved":sum(bool(r["provider_route"]) for r in result)},indent=2)+"\n")
    validate_collection(result,"pilot")
    print(json.dumps({"route_coverage":sum(bool(r["provider_route"]) for r in result),
          "rows":len(result),"issues":len(issues),"no_paid_calls":True}))
    return 0 if all(x["provider_route"] for x in result) else 2
if __name__=="__main__":
    sys.exit(main())
