#!/usr/bin/env python3
"""One-shot, budget-capped V3 external-model methods critiques via OpenRouter.

Four independent model families review overall methodology; Claude Sonnet separately
reviews each of 60 main + six new CAL3 case pairs. OFFLINE mock tests by default.
No v3 behavioral experiment inference; no human review approval implied.
"""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,math,os,re,sys,time
import urllib.request,urllib.error
from pathlib import Path
from v3_delegated_choice import ROOT,build,load_sources,DOMAIN_NOTES,OUTCOME_NOTE,SYSTEM_MESSAGE
from main_v2_matched_design import PATTERNS
from pilot_compatibility import key_preflight

OUTPUT=ROOT/"results"/"private"/"v3-external-reviews"
STATE=OUTPUT/"checkpoint.json"
PUBLIC=ROOT/"docs"
BUDGET_GLOBAL_USD=8.0
PAST_REPORTED=0.59845164
PAST_UNKNOWN_HOLD=0.42
REVIEW_NEW_CAP=5.50
CHARS_PER_INPUT_TOKEN_UPPER=1
REVIEW_MODELS=[
    {"model":"anthropic/claude-opus-5.5","input":4,"output":20,"max_tokens":5000,"effort":"high"},
    {"model":"openai/gpt-6-astra","input":10,"output":50,"max_tokens":5000,"effort":"high"},
    {"model":"qwen/qwen3.8-max-0902","input":2,"output":6,"max_tokens":5000,"effort":"high"},
    {"model":"x-ai/grok-4.7","input":1.6,"output":4.8,"max_tokens":5000,"effort":"high"},
]
CASE_MODEL={"model":"anthropic/claude-sonnet-5.5","input":2,"output":10,
            "max_tokens":1350,"effort":"low"}

def now(): return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
def hash_text(s):return hashlib.sha256(s.encode("utf-8")).hexdigest()
def atomic_write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(".tmp")
    with temp.open("w",encoding="utf-8") as fh:
        json.dump(obj,fh,ensure_ascii=False,indent=2)
        fh.flush();os.fsync(fh.fileno())
    os.replace(temp,path)
def transport(path,body=None):
    key=os.environ.get("OPENROUTER_API_KEY","")
    if len(key)<12:raise RuntimeError("MISSING_OPENROUTER_KEY")
    header={"Authorization":"Bearer "+key,"Accept":"application/json",
            "User-Agent":"llm-priority-audit-v3-review"}
    if body is not None:header["Content-Type"]="application/json"
    req=urllib.request.Request("https://openrouter.ai/api/v1"+path,
          data=None if body is None else json.dumps(body,ensure_ascii=False).encode("utf-8"),
          headers=header,method="GET" if body is None else "POST")
    try:
        with urllib.request.urlopen(req,timeout=210) as resp:
            return json.loads(resp.read(4_000_000))
    except urllib.error.HTTPError as e:
        raise RuntimeError("OPENROUTER_HTTP_"+str(e.code)) from None
    except (urllib.error.URLError,TimeoutError,OSError):
        raise RuntimeError("UNCERTAIN_TRANSPORT_ERROR") from None

def model_catalog():
    response=transport("/models")
    rows=response.get("data")
    if not isinstance(rows,list):raise RuntimeError("INVALID_MODEL_CATALOG")
    by={m.get("id"):m for m in rows if isinstance(m,dict)}
    for conf in REVIEW_MODELS+[CASE_MODEL]:
        m=by.get(conf["model"])
        if not m:raise RuntimeError("MODEL_NOT_IN_CATALOG_"+conf["model"])
        prices=m.get("pricing") or {}
        try:
            actual_in=float(prices["prompt"])*1_000_000
            actual_out=float(prices["completion"])*1_000_000
        except (ValueError,TypeError,KeyError):raise RuntimeError("MODEL_PRICE_UNKNOWN_"+conf["model"])
        if not (0<=actual_in<=conf["input"]*1.1 and 0<=actual_out<=conf["output"]*1.1):
            raise RuntimeError("MODEL_PRICE_ABOVE_ASSUMPTION_"+conf["model"])
    return True

def reserved_cost(prompt,conf):
    # Intentionally pessimistic estimate for English prompts: one token per char
    # plus 800 input overhead, and 2x the maximum completion tokens to account
    # for possible separately billed reasoning output/timing ambiguities.
    price=(len(prompt)+800)*conf["input"]/1e6 + (conf["max_tokens"]*2)*conf["output"]/1e6
    return round(price*1.35,8)

def method_prompt():
    # Independent review: no prior model outputs, earlier critique text, or favoured sign.
    proto=(ROOT/"docs"/"31-v3-delegated-choice-redesign.md").read_text(encoding="utf-8")
    proto=proto.split("## Existing budget and status")[0]
    examples=build("main")
    by={(r["domain"],r["frame"],r["q_quality_minus_n"],r["layout"]):r
        for r in examples if r["family_id"] in ("CONT-001","REVR-001","VERF-001")}
    sample=[]
    for domain in ("continuation","reversibility","verification"):
        for frame in ("salient","plain"):
            row=by[(domain,frame,-4,"layout0")]
            sample.append("DOMAIN: "+domain+" FRAME: "+("X" if frame=="salient" else "Y")+
                     "\nSYSTEM: "+row["system_message"]+"\nUSER: "+row["user_message"])
    mech=[]
    for idx,(name,actions) in enumerate(PATTERNS.items(),1):
        mech.append(f'Mechanism {idx}: {name}\nX action 1: {actions["Q"]}\n'
                    f'X action 2: {actions["N"]}\nY action 1: {actions["q"]}\n'
                    f'Y action 2: {actions["n"]}')
    return (
       "You are acting as an external MODEL reviewer of a newly proposed research design. "
       "Review it independently from the authors. You are not told how previous studies "
       "performed, the desired hypothesis direction or anyone else's assessment. "
       "This is a method-review task, not a prompt to produce actions for the proposed experiment. "
       "Give your own critical, technically rigorous assessment without a forced verdict, rubric "
       "or score. Assess whether the operationalized claim is meaningful and causally identifiable; "
       "whether the SAME material acts are truly preserved under X/Y descriptions; hidden asymmetries "
       "in risk, cost, utility, instruction/authority, framing and lexical valence; the soundness of "
       "delegation and measured quality tradeoffs; whether three domains can be aggregated; the "
       "proposed -4 primary contrast, label/order balancing, within-mechanism dependence and small "
       "cluster inference; whether the heldout calibration actually detects the relevant measurement "
       "failure; how you would distinguish revealed procedural inclination from mere task/language "
       "preferences; and what specific changes are essential before paid calibration or a 6,000-call main. "
       "Consider the strongest argument AGAINST publishing the proposal as planned. "
       "Do not assume a positive effect should be found or that a null is evidence of absence. "
       "Please be specific and independent; use illustrative examples grounded in exact prompt text. "
       "Aim for 800-1,250 words of final answer and state unresolved uncertainties. "
       "The synthetic power claims below should be treated as unverified assumptions.\n\n"
       "PROSPECTIVE DESIGN TEXT:\n"+proto+"\n\n"
       "SIX EXACT MODEL-FACING PROMPTS (these sample two descriptions in each domain):\n"+
       "\n\n".join(sample)+"\n\n"
       "FIFTEEN UNDERLYING PAIRED ACTION PATTERNS (labels X/Y are arbitrary for review):\n"+
       "\n\n".join(mech)
    )

def case_prompts():
    trial_map={}
    for phase in ("main","calibration"):
        for t in build(phase):
            if t["q_quality_minus_n"]==-4 and t["layout"]=="layout0":
                trial_map[t["family_id"],t["frame"]]=t
    families=[("main",x) for x in load_sources("main")]+[
              ("calibration",x) for x in load_sources("calibration")]
    prompts=[]
    for phase,f in families:
        a=trial_map[f["family_id"],"salient"]
        b=trial_map[f["family_id"],"plain"]
        swap=int(hash_text("v3-semantic-review-"+f["family_id"]),16)%2
        x,y=(b,a) if swap else (a,b)
        prompt=(
           "You are an independent MODEL reviewer of one new paired scenario. "
           "This review is blind to prior model behavior, the researcher's preferred "
           "outcome, and other reviewers. The two variants aim to describe the SAME "
           "material pair of actions with different verbal emphasis. The model "
           "receiving the prompt is genuinely delegated to choose rather than told "
           "which option to select. We will vary Q-minus-N measured task quality "
           "over -10, -4, 0, +4 and +10 points; both arms of a comparison share "
           "identical numeric outcomes and action-to-letter mappings. "
           "Review these two versions OPEN-ENDEDLY, in roughly 160-250 words. "
           "Inspect whether each version contains the same actual options, "
           "whether the context and assumptions cohere with both; whether it is "
           "legitimate to measure choice as a tradeoff; whether there are implicit "
           "costs or risks and whether style/default/valence varies accidentally; "
           "note any factual inconsistency between the two. "
           "Do not issue a token KEEP/REVISE/REJECT by default; do not optimize "
           "towards a favorable treatment effect or merely mirror these prompts. "
           "State any specific edit needed, or explain if the contrast is defensible.\n\n"
           "SYSTEM MESSAGE FOR BOTH VERSIONS:\n"+SYSTEM_MESSAGE+"\n\n"
           "VERSION X USER MESSAGE:\n"+x["user_message"]+"\n\n"
           "VERSION Y USER MESSAGE:\n"+y["user_message"]
        )
        prompts.append({"phase":phase,"family_id":f["family_id"],"prompt":prompt,
                        "prompt_sha256":hash_text(prompt),"blind_order_swapped":bool(swap)})
    assert len(prompts)==66
    return prompts

def preview():
    a=method_prompt()
    b=case_prompts()
    planned=sum(reserved_cost(a,m) for m in REVIEW_MODELS)+sum(
        reserved_cost(x["prompt"],CASE_MODEL) for x in b)
    return {"overall_models":[x["model"] for x in REVIEW_MODELS],
            "case_model":CASE_MODEL["model"],"case_count":len(b),
            "method_prompt_characters":len(a),"sample_case_prompt_characters":len(b[0]["prompt"]),
            "total_theoretical_all_calls_reserve_usd":round(planned,4),
            "review_incremental_cap_usd":REVIEW_NEW_CAP,
            "past_worst_allocation_usd":PAST_REPORTED+PAST_UNKNOWN_HOLD,
            "global_cap_usd":BUDGET_GLOBAL_USD}

def start_state():
    if STATE.exists():
        raise RuntimeError("PRIOR_REVIEW_CHECKPOINT_EXISTS_NO_AUTOMATIC_RETRY")
    OUTPUT.mkdir(parents=True,exist_ok=True)
    x={"created_utc":now(),"status":"IN_PROGRESS","review_type":"EXTERNAL_MODEL_NOT_HUMAN",
       "old_study_known_cost_usd":PAST_REPORTED,"old_study_reserved_liability_usd":PAST_UNKNOWN_HOLD,
       "new_cap_usd":REVIEW_NEW_CAP,"known_cost_usd":0.0,"unknown_liability_reserved_usd":0.0,
       "records":[],"inflight":None,"no_prior_experimental_responses_in_prompts":True,
       "no_behavioural_experiment_calls":True,"independent_human_signoffs":0}
    atomic_write(STATE,x);return x

def one_review(state,plan,conf):
    prompt=plan["prompt"]
    held=reserved_cost(prompt,conf)
    if state["known_cost_usd"]+state["unknown_liability_reserved_usd"]+held>REVIEW_NEW_CAP:
        raise RuntimeError("STOP_REVIEW_SPENDING_CAP")
    if PAST_REPORTED+PAST_UNKNOWN_HOLD+state["known_cost_usd"]+state["unknown_liability_reserved_usd"]+held>BUDGET_GLOBAL_USD:
        raise RuntimeError("STOP_GLOBAL_STUDY_CAP")
    if key_preflight(transport("/key"))["remaining_usd"]<held:
        raise RuntimeError("STOP_KEY_BALANCE_INSUFFICIENT")
    label=plan["label"]
    state["inflight"]={"label":label,"held_usd":held,"prompt_sha256":hash_text(prompt),"started_utc":now()}
    atomic_write(STATE,state)
    data=None;err=None
    try:
        data=transport("/chat/completions",{
          "model":conf["model"],
          "messages":[{"role":"user","content":prompt}],
          "max_tokens":conf["max_tokens"],
          "reasoning":{"effort":conf["effort"]},
          "provider":{"allow_fallbacks":False,"max_price":{
              "prompt":conf["input"]*1.1,"completion":conf["output"]*1.1}},
          "usage":{"include":True},
        })
    except Exception as exc:
        err=type(exc).__name__+":"+str(exc)[:60]
    record={"label":label,"model_requested":conf["model"],"prompt":prompt,
            "prompt_sha256":hash_text(prompt),"phase":plan["phase"],
            "family_id":plan.get("family_id"),"held_usd":held,
            "raw_response":data,"attempt_error":err,"finished_utc":now()}
    cost=((data or {}).get("usage") or {}).get("cost") if isinstance(data,dict) else None
    good_cost=type(cost) in (int,float) and math.isfinite(cost) and 0<=cost<=held
    record["known_cost_usd"]=float(cost) if good_cost else None
    if good_cost:state["known_cost_usd"]+=float(cost)
    else:state["unknown_liability_reserved_usd"]+=held
    msg=(((data or {}).get("choices") or [{}])[0].get("message") or {}) if isinstance(data,dict) else {}
    answer=msg.get("content")
    model_returned=data.get("model") if isinstance(data,dict) else None
    record["returned_model"]=model_returned
    if isinstance(answer,str) and len(answer.strip())>=90 and good_cost and not (data or {}).get("error"):
        record["review_text"]=answer.strip()
        record["status"]="COMPLETE"
    else:
        record["status"]="UNUSABLE_OR_UNRECONCILED"
    state["records"].append(record)
    state["inflight"]=None
    atomic_write(STATE,state)
    print(json.dumps({"review":label,"model":conf["model"],"status":record["status"],
       "known_cost_usd":record["known_cost_usd"],"held_usd":held,
       "total_completed":sum(r["status"]=="COMPLETE" for r in state["records"])}),flush=True)
    if not good_cost:
        raise RuntimeError("STOP_UNRECONCILED_CHARGE_NO_RETRY")
    return record

def publish(state):
    PUBLIC.mkdir(parents=True,exist_ok=True)
    lines=[
      "# V3 raw external-model methodological reviews",
      "",
      "Generated from original OpenRouter responses; **external AI-model opinions, NOT human independent peer review**.",
      "No original v1/v2 behavior results or other reviewer opinions were included in the prompts.",
      "Unapproved candidate v3 protocol only; all model output is critique, **zero new model-choice experimental trials**.",
      "",
      "## Overview",
      "",
      "| Requested model | Scope | Status | Known reported cost (USD) |",
      "|---|---|---|---|"
    ]
    for r in state["records"]:
        if r["phase"]=="overall":
            lines.append("| "+r["model_requested"]+" | Overall methodological review | "+r["status"]+
                         " | "+str(r["known_cost_usd"])+" |")
    lines.extend(["","## Individual critiques",""])
    for r in state["records"]:
        lines.extend(["### "+r["label"],"",
          "Requested model: `"+r["model_requested"]+"`.",
          "Prompt SHA-256: `"+r["prompt_sha256"]+"`.",
          "Reported cost (USD): "+str(r["known_cost_usd"])+".",
          "Response status: **"+r["status"]+"**.", "",
          r.get("review_text") or ("No usable review response recorded. "+str(r.get("attempt_error") or "")),
          ""])
    (PUBLIC/"33-v3-external-model-review-archive.md").write_text("\n".join(lines),encoding="utf-8")
    by_domain={}
    def concern_preview(txt):
        return " ".join(txt.replace("\n"," ").split())[:380]
    detailed=[]
    for r in state["records"]:
        if r["phase"]=="case":
            detailed.append({"family_id":r["family_id"],"status":r["status"],
                 "model":r["model_requested"],"reported_cost":r["known_cost_usd"],
                 "review_excerpt":concern_preview(r.get("review_text") or ""),
                 "review_full_text_available_in_raw_archive":True})
    overall=[r for r in state["records"] if r["phase"]=="overall"]
    completed=sum(r["status"]=="COMPLETE" for r in state["records"])
    report={
      "status":state["status"],"created_utc":state["created_utc"],
      "updated_utc":now(),"independent_human_reviews":0,
      "external_model_review_count":completed,"overall_attempted":len(overall),
      "overall_usable":sum(r["status"]=="COMPLETE" for r in overall),
      "scenario_attempted":len(detailed),
      "scenario_usable":sum(r["status"]=="COMPLETE" for r in state["records"] if r["phase"]=="case"),
      "new_known_cost_usd":round(state["known_cost_usd"],8),
      "new_unknown_liability_reserved_usd":round(state["unknown_liability_reserved_usd"],8),
      "conservative_total_research_allocation_usd":round(PAST_REPORTED+PAST_UNKNOWN_HOLD+
        state["known_cost_usd"]+state["unknown_liability_reserved_usd"],8),
      "main_study_authorized":False,"paid_v3_behavioral_calls":0,
      "family_excerpts":detailed,
    }
    (PUBLIC/"34-v3-external-review-accounting.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return report

class MockTransport:
    def __init__(self):self.count=0
    def request(self,path,body=None):
        if path=="/key":return {"data":{"limit":50,"limit_remaining":50,"is_management_key":False}}
        if path=="/models":return {"data":[{"id":m["model"],"pricing":{
            "prompt":str(m["input"]/1e6),"completion":str(m["output"]/1e6)}}
            for m in REVIEW_MODELS+[CASE_MODEL]]}
        if path=="/chat/completions":
            self.count+=1
            return {"model":body["model"],"usage":{"cost":0.002},
                    "choices":[{"message":{"content":"Both options are materially comparable under the written constraints, but the framing may alter attention to the workflow feature. Distinguish those psychological salience effects from stable preferences, and investigate possible asymmetries in the scenario context before approving the causal design. The primary estimand requires further review."}}]}
        raise AssertionError(path)

def run_live():
    pre=preview()
    print(json.dumps({"preflight_plan":pre}),flush=True)
    if pre["total_theoretical_all_calls_reserve_usd"]>REVIEW_NEW_CAP:
        raise RuntimeError("ALL_CALL_RESERVATIONS_EXCEED_CAP")
    key_preflight(transport("/key"))
    model_catalog()
    state=start_state()
    overall=method_prompt()
    plan=[{"label":"overall-"+str(i+1)+"-"+conf["model"],"phase":"overall","prompt":overall,"conf":conf}
          for i,conf in enumerate(REVIEW_MODELS)]
    plan.extend({"label":"case-"+x["family_id"],"phase":"case",
                 "family_id":x["family_id"],"prompt":x["prompt"],"conf":CASE_MODEL}
                for x in case_prompts())
    try:
        for item in plan:
            one_review(state,item,item["conf"])
        state["status"]="COMPLETE" if len(state["records"])==len(plan) else "PARTIAL"
    except Exception as exc:
        state["status"]="STOP_"+str(exc)[:120]
    finally:
        atomic_write(STATE,state)
        publish(state)
    return state

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("preview","mock","live"),required=True)
    args=ap.parse_args()
    if args.mode=="preview":
        print(json.dumps(preview(),indent=2));return 0
    if args.mode=="mock":
        # Static, charged-request-free checks; no secret lookup.
        p=preview()
        assert p["case_count"]==66 and len(p["overall_models"])==4
        assert p["total_theoretical_all_calls_reserve_usd"]<REVIEW_NEW_CAP
        assert len(set(p["overall_models"]))==4
        print("MOCK INPUT VALIDATION PASSED")
        return 0
    state=run_live()
    print(json.dumps({"status":state["status"],
      "attempted":len(state["records"]),
      "complete":sum(r["status"]=="COMPLETE" for r in state["records"]),
      "known_usd":state["known_cost_usd"],"unknown_held_usd":state["unknown_liability_reserved_usd"]}),
      flush=True)
    return 0 if state["status"]=="COMPLETE" else 2

if __name__=="__main__":sys.exit(main())
