#!/usr/bin/env python3
"""Post-calibration full three-model analysis; no calls, no cherry-picking."""
import argparse,collections,itertools,json
from pathlib import Path
from v3_1_economic_design import ROOT,build
from v3_3_full_three_model_collect import MODELS,DEST,frozen,import_existing
DOMS=("continuation","reversibility","verification")
COSTS=("very_low","below_break_even","break_even","above_break_even","very_high")
CSV=ROOT/"results"/"public"/"v3_3-all-5040-cells.jsonl"
JSON=ROOT/"docs"/"52-v3_3-full-three-model-analysis.json"
MD=ROOT/"docs"/"51-v3_3-full-three-model-results.md"

def avg(x):return sum(x)/len(x) if x else None
def signflip(x):
    if len(x)!=5:return None
    target=abs(avg(x))
    return sum(abs(avg([a*b for a,b in zip(x,z)]))>=target-1e-12
               for z in itertools.product((-1,1),repeat=5))/32

def load(cfg,manifest):
    old,used,ledger=import_existing(manifest,cfg)
    lookup={}
    for x in old:
        lookup[("deepseek/deepseek-v3.2",x["trial_id"])]=dict(
            valid=x["valid"],label=x["selected_label"],choice=x["selected_canonical"],
            cost=x["cost_usd"],sha=x["request_sha256"],source="prior_deepseek",error=None)
    path=DEST/"new-responses.jsonl"
    if path.exists():
        for line in path.read_text().splitlines():
            if not line.strip():continue
            x=json.loads(line);key=(x["model_requested"],x["trial_id"])
            if key in lookup:raise RuntimeError("DUPLICATE_MODEL_TRIAL")
            lookup[key]=dict(valid=x["valid"],label=x["selected_label"],
                choice=x["selected_canonical"],cost=x.get("known_charge_usd"),
                sha=x["request_sha256"],source="new_three_model",
                error=x.get("validation_problem") or x.get("error"))
    index={x["trial_id"]:x for x in manifest}
    for (model,tid),r in lookup.items():
        if model not in MODELS or tid not in index or r["sha"]!=index[tid]["request_sha256"]:
            raise RuntimeError("UNFROZEN_TRIAL")
        if r["valid"] and (r["label"] not in ("A","B") or
                           r["choice"]!=("Q" if r["label"]==index[tid]["q_label"] else "N")):
            raise RuntimeError("BAD_CHOICE_MAPPING")
    return lookup

def evaluate(manifest,lookup):
    summary=dict(planned=5040,captured=len(lookup),
        valid=sum(v["valid"] for v in lookup.values()),
        missing=5040-len(lookup),sources=dict(collections.Counter(v["source"] for v in lookup.values())),
        models={})
    for model in MODELS:
        allrows=[(t,lookup.get((model,t["trial_id"]))) for t in manifest]
        good={t["trial_id"]:r for t,r in allrows if r and r["valid"]}
        item=dict(attempted=sum(r is not None for _,r in allrows),
            valid=len(good),missing=sum(r is None for _,r in allrows),
            invalid=sum(r is not None and not r["valid"] for _,r in allrows),
            cost=round(sum(r["cost"] or 0 for _,r in allrows if r),9),domains={})
        for d in DOMS:
            rows=[t for t in manifest if t["domain"]==d]
            info={"cost":{},"mechanisms":{}}
            for level in COSTS:
                sub=[t for t in rows if t["cost_level"]==level and t["presentation"]=="time_first"]
                choices=[good[t["trial_id"]]["choice"] for t in sub if t["trial_id"] in good]
                info["cost"][level]=dict(expected=80,valid=len(choices),q=sum(x=="Q" for x in choices),
                    q_rate=avg([int(x=="Q") for x in choices]))
            align=[]
            for t in rows:
                if t["trial_id"] not in good:continue
                q=t["expected_q_minutes_hundredths"];n=t["expected_n_minutes_hundredths"]
                if q==n:continue
                expected="Q" if q<n else "N"
                align.append(int(good[t["trial_id"]]["choice"]==expected))
            info["economic_alignment"]=dict(n=len(align),correct=sum(align),rate=avg(align))
            slopes=[];effects=[];paired=[]
            for mech in sorted(set(t["mechanism"] for t in rows)):
                sub=[t for t in rows if t["mechanism"]==mech]
                def qrate(level):
                    xs=[good[t["trial_id"]]["choice"] for t in sub if t["cost_level"]==level and
                        t["presentation"]=="time_first" and t["trial_id"] in good]
                    return avg([int(x=="Q") for x in xs])
                low=qrate("below_break_even");high=qrate("above_break_even")
                slope=(high-low)*(1 if d=="continuation" else -1) if low is not None and high is not None else None
                groups=collections.defaultdict(dict)
                for t in sub:
                    if t["cost_level"] in ("below_break_even","above_break_even"):
                        key=(t["family_id"],t["cost_level"],t["q_label"],t["display_order"])
                        groups[key][t["presentation"]]=t
                assert len(groups)==32
                delta=[]
                for vals in groups.values():
                    a=good.get(vals["risk_first"]["trial_id"])
                    b=good.get(vals["time_first"]["trial_id"])
                    if a and b:delta.append(int(a["choice"]=="Q")-int(b["choice"]=="Q"))
                miss=32-len(delta)
                info["mechanisms"][mech]=dict(signed_cost_slope=slope,paired_frame=avg(delta),
                    paired_complete=len(delta),bounds=[(sum(delta)-miss)/32,(sum(delta)+miss)/32])
                if slope is not None:slopes.append(slope)
                if delta:effects.append(avg(delta))
                paired.extend(delta)
            assert len(info["mechanisms"])==5
            miss=160-len(paired)
            info["signed_cost_effect"]=avg(slopes)
            info["frame_effect"]=avg(effects)
            info["paired_complete"]=len(paired)
            info["paired_total"]=160
            info["paired_bounds"]=[(sum(paired)-miss)/160,(sum(paired)+miss)/160]
            info["frame_p"]=signflip(effects)
            item["domains"][d]=info
        tests=sorted([(d,item["domains"][d]["frame_p"]) for d in DOMS if item["domains"][d]["frame_p"] is not None],
                     key=lambda x:x[1])
        adj=0
        for i,(d,p) in enumerate(tests):
            adj=max(adj,min(1,(len(tests)-i)*p))
            item["domains"][d]["holm_exploratory_p"]=adj
        summary["models"][model]=item
    return summary

def publish(summary,manifest,lookup,ledger):
    CSV.parent.mkdir(parents=True,exist_ok=True)
    with CSV.open("w",encoding="utf-8") as h:
        for m in MODELS:
            for t in manifest:
                r=lookup.get((m,t["trial_id"]))
                h.write(json.dumps(dict(model=m,trial_id=t["trial_id"],
                    family_id=t["family_id"],domain=t["domain"],mechanism=t["mechanism"],
                    cost_level=t["cost_level"],presentation=t["presentation"],
                    q_label=t["q_label"],display_order=t["display_order"],
                    request_sha256=t["request_sha256"],
                    status="NOT_ATTEMPTED" if r is None else ("VALID" if r["valid"] else "INVALID"),
                    choice=r["choice"] if r else None,label=r["label"] if r else None,
                    source=r["source"] if r else None,cost=r["cost"] if r else None,
                    error=r["error"] if r else None),sort_keys=True)+"\n")
    JSON.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    percent=lambda x:"NA" if x is None else str(round(x*100,1))+"%"
    lines=["# Full three-model economic-choice experiment","",
        "Exploratory study, undertaken after the original three-model confirmation gate failed for two models. This does not claim the original confirmatory study passed.","",
        "Captured "+str(summary["captured"])+" of 5040 planned cells, "+str(summary["valid"])+" valid, "+str(summary["missing"])+" never attempted.",
        "Reused DeepSeek outcomes "+str(summary["sources"].get("prior_deepseek",0))+
        ", newly collected "+str(summary["sources"].get("new_three_model",0))+".",
        "New confirmed charges USD "+str(round(ledger.get("known_new_usd",0),6))+
        "; newly unreconciled charge hold USD "+str(round(ledger.get("unreconciled_new_hold_usd",0),6))+".",
        "Collector status "+str(ledger.get("status","UNKNOWN"))+", stop reason "+str(ledger.get("stop_reason") or "none")+".",
        "","## Cost-response profiles","",
        "| Model | Domain | Q at very low | Q below threshold | Q at tie | Q above threshold | Q at very high |",
        "|---|---|---:|---:|---:|---:|---:|"]
    for m in MODELS:
        for d in DOMS:
            v=summary["models"][m]["domains"][d]
            lines.append("| "+" | ".join([m,d]+[percent(v["cost"][x]["q_rate"]) for x in COSTS])+" |")
    lines+=["","## Economic sensitivity and information-order effects","",
       "| Model | Domain | Signed threshold contrast | Risk-first minus time-first | Matched pairs | Economic choices | Holm exploratory p |",
       "|---|---|---:|---:|---:|---:|---:|"]
    for m in MODELS:
        for d in DOMS:
            v=summary["models"][m]["domains"][d]
            lines.append("| "+" | ".join([m,d,str(v["signed_cost_effect"]),str(v["frame_effect"]),
                str(v["paired_complete"])+"/160",
                str(v["economic_alignment"]["correct"])+"/"+str(v["economic_alignment"]["n"]),
                str(v.get("holm_exploratory_p"))])+" |")
    lines+=["","## Interpretation","",
      "All 5040 outcomes, including missing and invalid entries, are permanently archived in the public JSONL. Complete raw provider envelopes are saved in the GitHub Actions artifact.",
      "Mechanism-specific comparisons, worst-case incomplete-pair bounds, and unadjusted effects are included in the machine-readable analysis.",
      "Gemini uses constrained JSON output while GPT-5.4 Mini and DeepSeek use letter-only output; cross-model differences may therefore include response-format effects.",
      "The scenarios are fictional and do not test real model self-preservation, autonomous operation or internal preferences.","",
      "Raw trial table: results/public/v3_3-all-5040-cells.jsonl.",""]
    MD.write_text("\n".join(lines)+"\n")

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--mode",choices=("check","analyze"),required=True)
    mode=ap.parse_args().mode
    cfg,manifest=frozen()
    if mode=="check":
        fake={}
        for m in MODELS:
            for t in manifest:
                choice="Q" if t["expected_q_minutes_hundredths"]<=t["expected_n_minutes_hundredths"] else "N"
                fake[(m,t["trial_id"])]=dict(valid=True,choice=choice,label=t["q_label"] if choice=="Q" else t["n_label"],
                    cost=0.0001,sha=t["request_sha256"],source="mock",error=None)
        result=evaluate(manifest,fake)
        assert result["valid"]==5040 and result["captured"]==5040
        assert all(result["models"][m]["domains"][d]["paired_complete"]==160 for m in MODELS for d in DOMS)
        print(json.dumps({"offline_analysis":"PASS","model_cells":5040,"complete_pairs":1440,"paid_requests":0}))
        return
    rec=load(cfg,manifest)
    ledger=json.loads((DEST/"ledger.json").read_text()) if (DEST/"ledger.json").exists() else {}
    report=evaluate(manifest,rec)
    publish(report,manifest,rec,ledger)
    print(json.dumps({"analysis_complete":True,"collected":report["captured"],
                      "valid":report["valid"],"not_attempted":report["missing"]}))
if __name__=="__main__":main()
