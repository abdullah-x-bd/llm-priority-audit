#!/usr/bin/env python3
"""One fresh, open-ended, non-leading Opus critique of a prospective revised study.

No old pilot outputs or earlier critiques are passed; one request only.
Not human independent peer review or an automatic experimental approval.
"""
import argparse,hashlib,json,math,os,sys
from pathlib import Path
from expand_design import ROOT
from main_v2_matched_design import source_families,main_v2_manifest
from pilot_compatibility import Transport,key_preflight,APIProblem

MODEL="anthropic/claude-opus-4.7"
OUT=ROOT/"results"/"private"/"v2-final-methods-review.json"
MAX_OUTPUT=3000
MAX_COST=0.40
GLOBAL_STUDY_CAP=8.0
PREVIOUS_UPPER=0.51196256+0.225477+0.0904

def reviewer_prompt():
    fam=source_families()
    seen={}
    for f in fam:
        seen.setdefault(f["mechanism"],f)
    assert len(seen)==15
    trial=next(x for x in main_v2_manifest() if
               x["family_id"]=="VERF-001" and x["frame"]=="priority" and
               x["condition"]=="zero" and x["directive"]=="N" and
               x["layout"]=="layout0")
    lines=[]
    for i,f in enumerate(seen.values(),1):
        lines.append(f"{i}. Domain {f['domain']}, {f['mechanism']}. "
              f"Fictional context: {f['context']}\n"
              f"Version X option Q: {f['action_q']}\n"
              f"Version X option N: {f['action_n']}\n"
              f"Version Y option Q: {f['neutral_action_q']}\n"
              f"Version Y option N: {f['neutral_action_n']}")
    return (
      "Please provide an open-ended, independent-from-the-authors methodological "
      "critique of the following NEW candidate experiment. You have not seen prior "
      "reviews, model response results, or the authors' earlier experiments. "
      "Avoid approving or rejecting simply to be agreeable. State what the design "
      "can causally identify, the strongest remaining confounds, whether both "
      "versions truly retain the same material choice, and whether the operator "
      "conflict is meaningful and measurable. Distinguish intentional framing "
      "differences from accidental differences. Tell us what you would repair "
      "before committing money to a large experiment, including whether a small "
      "sensitivity calibration is needed. Consider the three domains individually. "
      "Do not assume a positive result is desirable. Give a cohesive critical "
      "assessment in natural prose, about 700-1100 words. No verdict labels or "
      "numerical scores are requested.\n\n"
      "Candidate question: Does describing the SAME two fictional procedural "
      "actions with more salient continuation, reversibility, or verification "
      "language change which action a language model chooses against a single "
      "clear operator letter directive, compared with less salient but materially "
      "matched wording? The payoff table also varies relative Q quality by +10, "
      "0 and -10. Each frame is balanced over directed substantive option and A/B "
      "display position. A later study would use 60 fictional contexts, four "
      "contexts per each of fifteen action patterns, with five specified models. "
      "No main model choices have been collected for these NEW wordings.\n\n"
      "Representative exact model-facing prompt:\n"+trial["system_message"]+
      "\n"+trial["user_message"]+"\n\n"
      "All 15 underlying action patterns below (X more salient, Y less salient; "
      "names are descriptive and do not imply any desired direction):\n\n"+
      "\n\n".join(lines)
    )

def reserve(p):
    return (len(p)+700)*5/1e6+MAX_OUTPUT*25/1e6

def execute(transport,mode):
    if OUT.exists():raise RuntimeError("ONE_CALL_ALREADY_ATTEMPTED_NO_RETRY")
    p=reviewer_prompt()
    held=reserve(p)
    if held>MAX_COST or PREVIOUS_UPPER+held>GLOBAL_STUDY_CAP:
        raise RuntimeError("BUDGET_GATE_BLOCKED")
    if mode=="live":key_preflight(transport.request("/key"))
    OUT.parent.mkdir(parents=True,exist_ok=True)
    state={"status":"inflight","model_requested":MODEL,
         "review_prompt_sha256":hashlib.sha256(p.encode()).hexdigest(),
         "review_prompt":p,"cost_reserved_usd":held,
         "no_prior_pilot_outputs_or_reviews_in_prompt":True,
         "not_independent_human_peer_review":True}
    OUT.write_text(json.dumps(state,indent=2),encoding="utf-8")
    try:
        res=transport.request("/chat/completions",{
           "model":MODEL,"messages":[{"role":"user","content":p}],
           "max_tokens":MAX_OUTPUT,"reasoning":{"effort":"medium"},
           "usage":{"include":True},
           "provider":{"max_price":{"prompt":5,"completion":25},
                       "allow_fallbacks":True}})
        state["response"]=res
        cost=(res.get("usage") or {}).get("cost")
        text=((res.get("choices") or [{}])[0].get("message") or {}).get("content")
        state["reported_cost_usd"]=cost
        state["review"]=text if isinstance(text,str) else None
        if type(cost) not in (float,int) or not math.isfinite(cost) or cost<0 or cost>held:
            state["status"]="COST_UNKNOWN_OR_ABOVE_RESERVED"
        elif res.get("error") or not isinstance(text,str) or len(text)<300:
            state["status"]="UNUSABLE_METHODS_REVIEW"
        else:state["status"]="complete"
    except APIProblem as e:state["status"]="HTTP_"+str(e.http_status)
    except Exception as e:state["status"]="ERROR_"+type(e).__name__
    OUT.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"status":state["status"],"cost":state.get("reported_cost_usd"),
                      "reserved":held,"response_chars":len(state.get("review") or "")}),flush=True)
    return 0 if state["status"]=="complete" else 2

class Mock:
    def request(self,path,body=None):
        return {"usage":{"cost":.1},"choices":[{"message":{"content":"A sufficiently long methodological critique that retains content distinctions. "*8}}]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--mode",choices=("mock","live"),required=True)
    args=ap.parse_args()
    if args.mode=="live":
        key=os.environ.get("OPENROUTER_API_KEY","")
        if len(key)<12:raise SystemExit("Missing key")
        srv=Transport(key)
    else:srv=Mock()
    sys.exit(execute(srv,args.mode))
if __name__=="__main__":main()
