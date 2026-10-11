#!/usr/bin/env python3
"""Merge original 5040 trials and 3360 new Haiku/Llama trials.

Missing and invalid responses stay visible. Descriptive domain and paired
information-order outcomes match the frozen finite-family definitions.
"""
from __future__ import annotations
import argparse,collections,itertools,json
from v3_1_economic_design import ROOT,build
from v3_4_collect_additional_models import MODELS,DEST,load_frozen,old_provenance

BASE=ROOT/"results"/"public"/"v3_3-all-5040-cells.jsonl"
OUT=ROOT/"results"/"public"/"v3_4-all-8400-five-model-cells.jsonl"
DATA=ROOT/"docs"/"54-v3_4-five-model-analysis.json"
REPORT=ROOT/"docs"/"53-v3_4-five-model-results.md"
ALL=("openai/gpt-5.4-mini",MODELS[0],"google/gemini-3.5-flash-lite",
     "deepseek/deepseek-v3.2",MODELS[1])
DOM=("continuation","reversibility","verification")
LEVELS=("very_low","below_break_even","break_even","above_break_even","very_high")

def avg(seq):return sum(seq)/len(seq) if seq else None

def flip5(seq):
    if len(seq)!=5:return None
    target=abs(avg(seq))
    return sum(abs(avg([a*b for a,b in zip(seq,z)]))>=target-1e-12
               for z in itertools.product((-1,1),repeat=5))/32

def merge(manifest,more):
    lookup={}
    for line in BASE.read_text(encoding="utf-8").splitlines():
        if not line.strip():continue
        r=json.loads(line)
        key=(r["model"],r["trial_id"])
        if key in lookup:raise RuntimeError("DUPLICATE_HISTORICAL")
        lookup[key]={"status":r["status"],"choice":r["choice"],
                     "label":r["label"],"source":"v3_3","cost":r.get("cost"),
                     "error":r.get("error"),"sha":r["request_sha256"]}
    if len(lookup)!=5040:raise RuntimeError("WRONG_IMPORTED_DATA_SIZE")
    for r in more:
        key=(r["model"],r["trial_id"])
        if key in lookup:raise RuntimeError("REPEATED_PAID_TRIAL")
        lookup[key]={"status":"VALID" if r["valid"] else "INVALID",
                     "choice":r["selected_canonical"],"label":r["response_letter"],
                     "source":"v3_4","cost":r.get("known_charge_usd"),
                     "error":r.get("issue") or r.get("provider_error"),
                     "sha":r["request_sha256"]}
    index={t["trial_id"]:t for t in manifest}
    for (model,tid),r in lookup.items():
        if model not in ALL or tid not in index or r["sha"]!=index[tid]["request_sha256"]:
            raise RuntimeError("SOURCE_DATA_HASH_OR_MODEL_MISMATCH")
        if r["status"]=="VALID":
            t=index[tid]
            if r["choice"] not in ("Q","N") or r["label"]!=(
                t["q_label"] if r["choice"]=="Q" else t["n_label"]):
                raise RuntimeError("SOURCE_CHOICE_NOT_VALID")
    return lookup

def compute(manifest,lookup):
    result={"planned":8400,"attempted":len(lookup),
            "valid":sum(r["status"]=="VALID" for r in lookup.values()),
            "not_attempted":8400-len(lookup),"models":{}}
    for model in ALL:
        item={"expected":1680,"attempted":sum((model,t["trial_id"]) in lookup for t in manifest),
              "valid":sum(lookup.get((model,t["trial_id"]),{}).get("status")=="VALID" for t in manifest),
              "by_domain":{}}
        valid={t["trial_id"]:lookup[(model,t["trial_id"])] for t in manifest
               if (model,t["trial_id"]) in lookup and lookup[(model,t["trial_id"])]["status"]=="VALID"}
        item["invalid"]=item["attempted"]-item["valid"]
        item["not_attempted"]=1680-item["attempted"]
        item["known_cost"]=round(sum(lookup.get((model,t["trial_id"]),{}).get("cost") or 0
                                     for t in manifest),9)
        for domain in DOM:
            rows=[t for t in manifest if t["domain"]==domain]
            d={"curve":{},"mechanisms":{}}
            for level in LEVELS:
                xs=[t for t in rows if t["cost_level"]==level and t["presentation"]=="time_first"]
                vals=[valid[t["trial_id"]]["choice"] for t in xs if t["trial_id"] in valid]
                d["curve"][level]={"planned":80,"valid":len(vals),
                    "q":sum(x=="Q" for x in vals),
                    "q_rate":avg([int(x=="Q") for x in vals])}
            controls=[]
            for t in rows:
                if t["trial_id"] not in valid:continue
                q=t["expected_q_minutes_hundredths"];n=t["expected_n_minutes_hundredths"]
                if q==n:continue
                controls.append(int(valid[t["trial_id"]]["choice"]==("Q" if q<n else "N")))
            d["economic_non_tie"]={"correct":sum(controls),"n":len(controls),"share":avg(controls)}
            slope=[];order=[];all_pairs=[]
            for mechanism in sorted(set(x["mechanism"] for x in rows)):
                z=[x for x in rows if x["mechanism"]==mechanism]
                def q_at(level):
                    subset=[valid[t["trial_id"]]["choice"] for t in z
                            if t["presentation"]=="time_first" and t["cost_level"]==level
                            and t["trial_id"] in valid]
                    return avg([int(x=="Q") for x in subset])
                lo=q_at("below_break_even");hi=q_at("above_break_even")
                direction=(hi-lo)*(1 if domain=="continuation" else -1) if lo is not None and hi is not None else None
                paired=collections.defaultdict(dict)
                for t in z:
                    if t["cost_level"] in ("below_break_even","above_break_even"):
                        key=(t["family_id"],t["cost_level"],t["q_label"],t["display_order"])
                        paired[key][t["presentation"]]=t
                if len(paired)!=32:raise RuntimeError("PAIR_DESIGN_CORRUPT")
                deltas=[]
                for pair in paired.values():
                    a=valid.get(pair["risk_first"]["trial_id"])
                    b=valid.get(pair["time_first"]["trial_id"])
                    if a and b:
                        deltas.append(int(a["choice"]=="Q")-int(b["choice"]=="Q"))
                miss=32-len(deltas)
                d["mechanisms"][mechanism]={
                    "signed_cost_response":direction,"paired_frame_effect":avg(deltas),
                    "pairs_observed":len(deltas),
                    "worst_case_bounds":[(sum(deltas)-miss)/32,(sum(deltas)+miss)/32]}
                if direction is not None:slope.append(direction)
                if deltas:order.append(avg(deltas))
                all_pairs.extend(deltas)
            assert len(d["mechanisms"])==5
            miss=160-len(all_pairs)
            d["signed_cost_effect"]=avg(slope)
            d["frame_effect_across_mechanisms"]=avg(order)
            d["frame_effect_across_pairs"]=avg(all_pairs)
            d["paired_complete"]=len(all_pairs)
            d["paired_planned"]=160
            d["paired_worst_case_bounds"]=[(sum(all_pairs)-miss)/160,(sum(all_pairs)+miss)/160]
            d["exploratory_signflip_p"]=flip5(order)
            item["by_domain"][domain]=d
        tests=sorted([(d,item["by_domain"][d]["exploratory_signflip_p"])
                      for d in DOM if item["by_domain"][d]["exploratory_signflip_p"] is not None],
                     key=lambda x:x[1])
        adj=0
        for i,(d,p) in enumerate(tests):
            adj=max(adj,min(1,(len(tests)-i)*p))
            item["by_domain"][d]["holm_exploratory_p"]=adj
        result["models"][model]=item
    return result

def publish(manifest,lookup,result,ledger):
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open("w",encoding="utf-8") as out:
        for m in ALL:
            for t in manifest:
                r=lookup.get((m,t["trial_id"]))
                row={"model":m,"trial_id":t["trial_id"],"family_id":t["family_id"],
                     "domain":t["domain"],"mechanism":t["mechanism"],
                     "cost_level":t["cost_level"],"q_label":t["q_label"],
                     "display_order":t["display_order"],"presentation":t["presentation"],
                     "request_sha256":t["request_sha256"],
                     "status":r["status"] if r else "NOT_ATTEMPTED",
                     "choice":r["choice"] if r else None,"label":r["label"] if r else None,
                     "source":r["source"] if r else None,
                     "known_charge_usd":r["cost"] if r else None,
                     "error":r["error"] if r else None}
                out.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n")
    DATA.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    pct=lambda x:"NA" if x is None else str(round(100*x,1))+"%"
    lines=[
        "# Five-model economic-choice experiment (complete factorial coverage)",
        "",
        "**Study type:** exploratory extension of the original three-model results after a failed all-model calibration gate. All old model responses remain unchanged.",
        "",
        f"**Attempted:** {result['attempted']:,}/8,400. **Valid:** {result['valid']:,}. **Unattempted:** {result['not_attempted']:,}.",
        f"**Additional Haiku and Llama known charges:** USD {ledger.get('new_known_usd',0):.6f}. **Additional unknown liability held:** USD {ledger.get('new_unknown_hold_usd',0):.6f}.",
        f"**Collector status:** {ledger.get('status','UNKNOWN')}. Stop reason: {ledger.get('stop_reason') or 'none'}.",
        "",
        "## Cost-response curves",
        "",
        "| Model | Domain | Q, very low cost | Q, below break-even | Q, tie | Q, above break-even | Q, very high cost | Valid total |",
        "|---|---|---:|---:|---:|---:|---:|---:|"
    ]
    for m in ALL:
        for domain in DOM:
            d=result["models"][m]["by_domain"][domain]
            valid=sum(lookup.get((m,t["trial_id"]),{}).get("status")=="VALID" for t in manifest if t["domain"]==domain)
            fields=[pct(d["curve"][x]["q_rate"]) for x in LEVELS]
            lines.append("| "+" | ".join([m,domain,*fields,f"{valid}/560"])+" |")
    lines+=["","## Matched framing effects and economic benchmarks","",
       "| Model | Domain | Signed cost effect | Risk-first versus time-first | Complete pairs | Correct minimum-work choice, non-ties | Holm exploratory p |",
       "|---|---|---:|---:|---:|---:|---:|"]
    for m in ALL:
        for domain in DOM:
            d=result["models"][m]["by_domain"][domain]
            x=d["economic_non_tie"]
            lines.append("| "+" | ".join([m,domain,str(d["signed_cost_effect"]),
                str(d["frame_effect_across_mechanisms"]),str(d["paired_complete"])+"/160",
                str(x["correct"])+"/"+str(x["n"])+" ("+pct(x["share"])+")",
                str(d.get("holm_exploratory_p"))])+" |")
    lines+=["","## Scientific limits","",
       "The 5,040-cell three-model study was completed first, and Haiku/Llama were added after those results were visible. Thus this is not an untouched five-model preregistration.",
       "The original GPT and Gemini calibration failures remain part of the record. Technical API-format and provider differences may contribute to between-model differences.",
       "Five mechanisms per domain and 60 authored fictional contexts do not justify universal conclusions about deployed agents or intrinsic model drives.",
       "Any invalid or unattempted call is retained in the permanent 8,400-row archive. Raw response envelopes and billing metadata live in GitHub Actions artifacts.",
       "This dataset includes null effects; no future study is automatically required solely because it is described as exploratory.",
       "",
       "## Reproducibility","",
       "- Exact frozen prompts: scripts/v3_1_economic_design.py and data/v3_1/context_inventory.jsonl.",
       "- Expansion registration: config/v3_4-five-model-expansion-freeze.json.",
       "- Complete row archive: results/public/v3_4-all-8400-five-model-cells.jsonl.",
       "- Machine-readable analysis: docs/54-v3_4-five-model-analysis.json.",
       ""]
    REPORT.write_text("\n".join(lines)+"\n")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("check","analyze"),required=True)
    mode=parser.parse_args().mode
    cfg,manifest=load_frozen()
    old_provenance(cfg)
    if mode=="check":
        allrows={}
        for m in ALL:
            for t in manifest:
                choice="Q" if t["expected_q_minutes_hundredths"]<=t["expected_n_minutes_hundredths"] else "N"
                allrows[(m,t["trial_id"])]={
                    "status":"VALID","choice":choice,
                    "label":t["q_label"] if choice=="Q" else t["n_label"],
                    "cost":0.0001,"source":"mock","error":None,
                    "sha":t["request_sha256"]}
        result=compute(manifest,allrows)
        assert result["valid"]==8400
        assert all(result["models"][m]["by_domain"][d]["paired_complete"]==160
                   for m in ALL for d in DOM)
        print(json.dumps({"offline":"PASS","five_models":True,
             "cells":8400,"paired_frames":2400,"no_paid_requests":True}))
        return
    current=(ROOT/"results"/"private"/"v3_4-resumed-collection")
    current=current if current.exists() else DEST
    file=current/"new-two-model-raw.jsonl"
    rows=[json.loads(x) for x in file.read_text().splitlines() if x.strip()] if file.exists() else []
    lookup=merge(manifest,rows)
    ledger=json.loads((current/"ledger.json").read_text()) if (current/"ledger.json").exists() else {}
    summary=compute(manifest,lookup)
    publish(manifest,lookup,summary,ledger)
    print(json.dumps({"attempted":summary["attempted"],"valid":summary["valid"],
        "missing":summary["not_attempted"],"cost_usd":ledger.get("new_known_usd")}),flush=True)
if __name__=="__main__":main()
