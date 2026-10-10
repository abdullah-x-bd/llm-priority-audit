#!/usr/bin/env python3
"""Deterministic public status summary; never calls an external API."""
from __future__ import annotations
import collections
import itertools
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"results"/"private"/"v3_1-single-shot"
TARGET=ROOT/"docs"/"44-v3_1-one-shot-results.md"
DOMAINS=("continuation","reversibility","verification")
MODELS=("openai/gpt-5.4-mini","google/gemini-3.5-flash-lite","deepseek/deepseek-v3.2")

def load(name):
    f=OUT/name
    return json.loads(f.read_text()) if f.exists() else None

def records(stage):
    p=OUT/(stage+"-responses.jsonl")
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []

def mean(x):
    return sum(x)/len(x) if x else None

def analyse(allrows):
    bymodel={}
    domains={}
    for model in MODELS:
        rows=[r for r in allrows if r["model_requested"]==model]
        bymodel[model]={"attempted":len(rows),"valid":sum(r["status"]=="VALID" for r in rows)}
        for d in DOMAINS:
            for lev in ("very_low","below_break_even","break_even","above_break_even","very_high"):
                x=[r for r in rows if r["status"]=="VALID" and r["domain"]==d
                   and r["cost_level"]==lev and r["presentation"]=="time_first"]
                bymodel[model][d+"/"+lev]={"n":len(x),"q":sum(r["selected_semantic_action"]=="Q" for r in x)}
    for domain in DOMAINS:
        drows=[r for r in allrows if r["domain"]==domain]
        mechs={}
        for mechanism in sorted(set(r["mechanism"] for r in drows)):
            pair=collections.defaultdict(dict)
            for r in drows:
                if r["mechanism"]!=mechanism or r["cost_level"] not in ("below_break_even","above_break_even"):
                    continue
                key=(r["model_requested"],r["family_id"],r["cost_level"],r["q_label"],r["display_order"])
                pair[key][r["presentation"]]=r
            deltas=[]
            for vals in pair.values():
                a=vals.get("risk_first");b=vals.get("time_first")
                if a and b and a["status"]=="VALID" and b["status"]=="VALID":
                    deltas.append(int(a["selected_semantic_action"]=="Q")-
                                  int(b["selected_semantic_action"]=="Q"))
            mechs[mechanism]={"complete_pairs":len(deltas),"order_effect":mean(deltas)}
        v=[x["order_effect"] for x in mechs.values() if x["order_effect"] is not None]
        p=None
        if len(v)==5:
            observed=abs(mean(v))
            signs=(itertools.product((-1,1),repeat=5))
            p=sum(abs(mean([a*b for a,b in zip(v,s)]))>=observed-1e-12 for s in signs)/32
        domains[domain]={"mechanisms":mechs,"mean_order_effect":mean(v),"sign_flip_p":p}
    validp=sorted((d,domains[d]["sign_flip_p"]) for d in DOMAINS if domains[d]["sign_flip_p"] is not None)
    last=0
    for idx,(d,p) in enumerate(sorted(validp,key=lambda x:x[1])):
        last=max(last,min(1,p*(len(validp)-idx)))
        domains[d]["holm_adjusted_exploratory_p"]=last
    return {"per_model":bymodel,"domains":domains,
            "caveat":"Finite authored-task descriptive effects; five mechanism clusters per domain. Exact sign-flip p values have coarse resolution and require unverified exchangeability. Holm adjusted values are exploratory, not deployment-population inferences."}

def main():
    cal=load("calibration-report.json")
    mn=load("main-report.json")
    ledger=load("spending-ledger.json")
    cr=records("calibration"); mr=records("main")
    status=(mn or {}).get("status") if mn else (
        "CALIBRATION_PASS_MAIN_NOT_FINISHED" if (cal or {}).get("passed_all_gates")
        else "CALIBRATION_NO_GO_OR_FAILED")
    lines=[
      "# V3.1 one-shot study execution and results",
      "",
      "**Status:** "+status,
      "Protocol frozen before requests: v3.1-2026-10-11-single-shot.",
      "An explicit participant letter is a prompted choice, not evidence of an internal model goal.",
      "",
      "| Stage | Planned calls | Captured attempts | Valid attributed answers |",
      "|---|---:|---:|---:|",
      "| Calibration | 864 | "+str(len(cr))+" | "+str(sum(x["status"]=="VALID" for x in cr))+" |",
      "| Main | 5,040 | "+str(len(mr))+" | "+str(sum(x["status"]=="VALID" for x in mr))+" |",
      "",
    ]
    if ledger:
        lines+=["New known charges $"+str(round(ledger["charged_usd"],7))+
                "; conservative unknown liability $"+str(round(ledger["held_unknown_usd"],7))+".",
                "Previously recorded known project charges $1.79190464, with prior $0.42 unresolved hold.",
                "No automatic model-call retries were performed.",""]
    if cal:
        lines+=["## Prespecified calibration","",
                "Automatic all-model gate: "+("PASS" if cal["passed_all_gates"] else "NO-GO")+".","",
                "| Model | Format validity | Arithmetic non-tie | Tie accuracy | Near threshold | Cost-response domains | Passed |",
                "|---|---:|---:|---:|---:|---:|---|"]
        for model in MODELS:
            x=cal["calibration_gates"].get(model,{})
            count=sum(v.get("pass",False) for v in x.get("cost_direction_by_domain",{}).values())
            lines.append("| "+" | ".join([
                model,str(x.get("valid_rate","NA")),str(x.get("non_tie_correct","NA")),
                str(x.get("tie_correct","NA")),str(x.get("near_threshold_correct","NA")),
                str(count)+"/3",str(x.get("passed",False))])+" |")
        lines+=["","Calibration budget forecast: "+json.dumps(cal.get("main_cost_preflight",{}),sort_keys=True),""]
    if mr:
        a=analyse(mr)
        (OUT/"prespecified-analysis.json").write_text(json.dumps(a,sort_keys=True,indent=2)+"\n")
        lines+=["## Main results","",
                "| Model | Domain | Cost level | Valid N | Q count | Q fraction |",
                "|---|---|---|---:|---:|---:|"]
        for model in MODELS:
            for domain in DOMAINS:
                for lev in ("very_low","below_break_even","break_even","above_break_even","very_high"):
                    x=a["per_model"][model][domain+"/"+lev]
                    n=x["n"]
                    lines.append("| "+" | ".join([
                        model,domain,lev,str(n),str(x["q"]),
                        format(x["q"]/n,".4f") if n else "missing"])+" |")
        lines+=["","## Presentation-order differences by domain","",
                "| Domain | Mean of available mechanism paired contrasts | Exploratory p | Holm adjusted exploratory p |",
                "|---|---:|---:|---:|"]
        for domain in DOMAINS:
            x=a["domains"][domain]
            lines.append("| "+domain+" | "+str(x["mean_order_effect"])+" | "+
                         str(x["sign_flip_p"])+" | "+str(x.get("holm_adjusted_exploratory_p"))+" |")
        lines+=["",a["caveat"],""]
    lines+=["## Disclosure","",
            "Prior AI-model methodological reviews assessed V3, not the final V3.1 prompts.",
            "No external human semantic signoff of V3.1 is claimed.",
            "No statistically significant result, expected direction or null conclusion was required for the main outcomes.",
            "The run artifacts retain every complete raw response, failed request, provider identity, metadata and billing observation.",
            ""]
    TARGET.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"status":status,"calibration_attempted":len(cr),
                       "main_attempted":len(mr),
                       "new_known_charges":ledger["charged_usd"] if ledger else None}),flush=True)

if __name__=="__main__":
    main()
