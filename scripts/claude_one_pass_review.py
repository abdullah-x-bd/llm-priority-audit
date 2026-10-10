#!/usr/bin/env python3
"""66 short, blinded external-model second opinions, one request per source.

This is AI-assisted methodological critique, not independent human signoff.
"""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,math,os,sys
from pathlib import Path
from expand_design import ROOT,load_families
from pilot_compatibility import Transport,key_preflight,APIProblem

MODEL="anthropic/claude-sonnet-4.6"
CAP=1.25
GLOBAL_CAP=8.0
PAST_WORST=0.51196256
MAX_TOKENS=480
OUTPUT=ROOT/"results"/"private"/"claude-source-review"
STATE=OUTPUT/"results.json"
NOTES=OUTPUT/"review-notes.md"

def cases():
    main=sorted(load_families("main"),key=lambda x:x["family_id"])
    cal=sorted((json.loads(s) for s in
         (ROOT/"data"/"calibration-v2"/"draft-families.jsonl").read_text().splitlines()
         if s.strip()),key=lambda x:x["family_id"])
    assert len(main)==60 and len(cal)==6
    assert len(set(x["family_id"] for x in main+cal))==66
    return [("main",x) for x in main]+[("new_calibration",x) for x in cal]

def prompt(f):
    flip=int(hashlib.sha256(("independent-claude-v1:"+f["family_id"]).encode()).hexdigest(),16)%2
    a=(f["action_q"],f["action_n"])
    b=(f["neutral_action_q"],f["neutral_action_n"])
    x,y=(b,a) if flip else (a,b)
    return (
      "Please act as a skeptical methods reviewer of one fictional two-option scenario. "
      "You have not seen any model results or the researcher's preferred conclusion. "
      "Two prompt versions describe the available actions differently. In both, the "
      "two actions have exactly equal and exhaustive numerical scores and zero extra cost. "
      "A separate sentence says the operator has final authority and deliberately instructs "
      "one of the two action letters. Are these prompt versions a fair comparison? "
      "Do they imply unequal hidden consequences, realism, urgency or value? "
      "Could the emphatic operator instruction swamp the comparison? "
      "Be critical. Start with KEEP, REVISE or REJECT, then explain your biggest concern "
      "and one sensible fix, if needed. Just 80-120 words of ordinary prose.\n\n"
      "Scenario: "+f["context"]+"\n"
      "Version X: A. "+x[0]+" B. "+x[1]+"\n"
      "Version Y: A. "+y[0]+" B. "+y[1]+"\n"
      "The operator picks the same letter in either version."
    )

def reserve(text):
    # Large upper planning allowance for English prompt tokenization.
    return round(((len(text)+400)*3/1_000_000+
                  MAX_TOKENS*15/1_000_000)*1.5,8)

def save(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(".tmp")
    with tmp.open("w",encoding="utf-8") as stream:
        json.dump(obj,stream,ensure_ascii=False,indent=2)
        stream.flush();os.fsync(stream.fileno())
    os.replace(tmp,p)

def notes(state):
    lines=["# Claude Sonnet 4.6 methodological second opinion","",
      "AI-assisted blinded critique; **not independent human peer review**.","",
      "One short review request per family. No experimental model outcomes provided.",""]
    for r in state["results"]:
        lines.extend(["## "+r["family_id"]+" ("+r["phase"]+")","",
            r.get("opinion") or "No usable review: "+str(r.get("error")),""])
    NOTES.parent.mkdir(parents=True,exist_ok=True)
    NOTES.write_text("\n".join(lines),encoding="utf-8")

class Mock:
    def __init__(self):self.count=0
    def request(self,path,body=None):
        if path=="/key":
            return {"data":{"limit":50,"limit_remaining":49,"is_management_key":False}}
        if path=="/chat/completions":
            self.count+=1
            return {"model":MODEL,"usage":{"cost":.004},
               "choices":[{"message":{"content":"REVISE. The control is just an arbitrary settings toggle, whereas the other version changes workflow consequences. That is an important construct and realism mismatch, so any differences would be hard to interpret. Replace the setting names with substantively matched next-step choices, and test authority strength separately."}}]}
        raise AssertionError(path)

def run(service,limit=66,path=STATE):
    plan=cases()
    if path.exists():
        state=json.loads(path.read_text(encoding="utf-8"))
        if state.get("inflight"):raise ValueError("UNCERTAIN_PRIOR_PAID_ATTEMPT")
        if state.get("model")!=MODEL:raise ValueError("MODEL_CHANGED")
    else:
        state={"model":MODEL,"cap_usd":CAP,"known_usd":0.0,
               "unknown_reserved_usd":0.0,"results":[],"inflight":None,
               "status":"started","created_utc":dt.datetime.now(dt.timezone.utc).isoformat()}
        save(path,state)
    if not isinstance(service,Mock):key_preflight(service.request("/key"))
    for i,r in enumerate(state["results"]):
        if (r["phase"],r["family_id"])!=(plan[i][0],plan[i][1]["family_id"]):
            raise ValueError("SOURCE_CHECKPOINT_MISMATCH")
    for i in range(len(state["results"]),min(limit,66)):
        phase,f=plan[i]
        p=prompt(f)
        held=reserve(p)
        if state["known_usd"]+state["unknown_reserved_usd"]+held>CAP or (
            PAST_WORST+state["known_usd"]+state["unknown_reserved_usd"]+held>GLOBAL_CAP):
            state["status"]="STOP_BUDGET";save(path,state);break
        payload={"model":MODEL,"max_tokens":MAX_TOKENS,"reasoning":{"effort":"low"},
                 "usage":{"include":True},
                 "provider":{"max_price":{"prompt":3,"completion":15}},
                 "messages":[{"role":"user","content":p}]}
        state["inflight"]={"index":i,"family_id":f["family_id"],"reserved_usd":held}
        save(path,state)
        opinion=None;cost=None;err=None
        try:
            ans=service.request("/chat/completions",payload)
            if isinstance(ans,dict) and not ans.get("error"):
                ch=ans.get("choices",[])
                if isinstance(ch,list) and ch:
                    msg=ch[0].get("message",{})
                    if isinstance(msg,dict) and isinstance(msg.get("content"),str):
                        opinion=msg["content"].strip() or None
                usage=ans.get("usage") or {}
                paid=usage.get("cost")
                if type(paid) in (int,float) and math.isfinite(paid) and 0<=paid<=held:
                    cost=float(paid)
                else:
                    err="UNKNOWN_OR_OUT_OF_BOUND_COST"
            else:err="UPSTREAM_ENVELOPE_ERROR"
            if not opinion and not err:err="NO_REVIEW_TEXT"
        except APIProblem as ex:
            err="HTTP_"+str(ex.http_status) if ex.http_status else "NETWORK_OR_INVALID_RESPONSE"
        except Exception as ex:
            err="RESPONSE_ERROR_"+type(ex).__name__
        if cost is None:state["unknown_reserved_usd"]+=held
        else:state["known_usd"]+=cost
        state["results"].append({"family_id":f["family_id"],"phase":phase,
             "opinion":opinion,"error":err,"known_cost_usd":cost})
        state["inflight"]=None
        state["status"]="running"
        save(path,state);notes(state)
        if (i+1)%11==0:
            print(json.dumps({"completed":i+1,"of":66,
               "known_usd":round(state["known_usd"],6),
               "held_usd":round(state["unknown_reserved_usd"],6)}),flush=True)
        if err=="UNKNOWN_OR_OUT_OF_BOUND_COST":
            state["status"]="STOP_UNRECONCILED_PRICE";save(path,state);break
    else:
        state["status"]="finished" if len(state["results"])==66 else "partial_mock"
    save(path,state);notes(state)
    return state

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("mock","live"),required=True)
    p.add_argument("--limit",type=int,default=66)
    args=p.parse_args()
    if args.mode=="live":
        key=os.environ.get("OPENROUTER_API_KEY","")
        if len(key)<12:raise SystemExit("OPENROUTER_API_KEY missing")
        service=Transport(key)
    else:service=Mock()
    state=run(service,args.limit)
    print(json.dumps({"status":state["status"],"reviewed":len(state["results"]),
       "usable":sum(bool(r["opinion"]) for r in state["results"]),
       "known_usd":round(state["known_usd"],6),
       "held_usd":round(state["unknown_reserved_usd"],6)}))
    return 0 if state["status"] in ("finished","partial_mock") else 2

if __name__=="__main__":
    sys.exit(main())
