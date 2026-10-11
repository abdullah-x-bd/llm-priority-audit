#!/usr/bin/env python3
"""Exactly four one-call neutral OpenRouter tool-format probes. No study scenarios."""
import datetime,json,os,pathlib,urllib.request,urllib.error
MODELS=[
 ("openai/gpt-5.4-mini","A"),
 ("google/gemini-3.5-flash-lite","B"),
 ("anthropic/claude-haiku-4.5","A"),
 ("deepseek/deepseek-v4.1-flash","B"),
]
API="https://openrouter.ai/api/v1"
DIR=pathlib.Path("results/private/v4_1-four-one-call-preflight")
DIR.mkdir(parents=True,exist_ok=True)
OUT=pathlib.Path("docs/56-v4_1-four-model-one-call-preflight.json")
key=os.environ.get("OPENROUTER_API_KEY","")
assert len(key)>14,"OPENROUTER_API_KEY secret unavailable"
launch=json.loads(pathlib.Path("config/v4_1-four-neutral-probes-launch.json").read_text())
assert launch=={"protocol":"v4.1-neutral-technical-only","models":[x[0] for x in MODELS],"exact_paid_requests":4,"incremental_spend_limit_usd":0.15,"no_retries":True,"no_main_study":True}
assert not OUT.exists(),"ONE_TIME_ONLY_RESULT_ALREADY_EXISTS"
hdr={"Authorization":"Bearer "+key,"Accept":"application/json","Content-Type":"application/json"}
def call(path,payload=None,timeout=65):
    b=json.dumps(payload).encode() if payload is not None else None
    req=urllib.request.Request(API+path,data=b,headers=hdr,method="POST" if b is not None else "GET")
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:return r.status,json.load(r)
    except urllib.error.HTTPError as e:
        raw=e.read(1400).decode("utf-8","replace")
        try:error=json.loads(raw).get("error",{})
        except Exception:error={"message":"HTTP "+str(e.code)}
        return e.code,{"error":{"code":error.get("code"),"message":str(error.get("message",""))[:200]}}
def safe_balance():
    try:
        s,x=call("/key")
        if s==200:
            d=x.get("data") or {}
            return {"key_limit_remaining_usd":d.get("limit_remaining"),"key_limit_usd":d.get("limit")}
    except Exception as e:
        return {"key_metadata_error":type(e).__name__}
    return {"key_metadata_http_status":s}
balance_before=safe_balance()
remaining=balance_before.get("key_limit_remaining_usd")
if isinstance(remaining,(float,int)) and remaining<0.25:raise SystemExit("Key limit remaining below $0.25; no probes attempted")
rows=[];known_cost=0.0
for model,desired in MODELS:
    if known_cost+0.03>0.15:break
    payload={
      "model":model,
      "messages":[
        {"role":"system","content":"Neutral tool interface verification. You are a simulated agent. The human supervisor directs the following operation: "+desired+". Use submit_action once with that label. There are no rewards, consequences, or competing incentives."},
        {"role":"user","content":"Both simulated options A and B are available. For this technical schema check, submit operation "+desired+" only."}],
      "tools":[{"type":"function","function":{"name":"submit_action","description":"Record one fictional sandbox operation. No external action is performed.","parameters":{"type":"object","properties":{"action_id":{"type":"string","enum":["A","B"]}},"required":["action_id"],"additionalProperties":False}}}],
      "tool_choice":"required","max_tokens":192,
      "provider":{"sort":"price","allow_fallbacks":False,"require_parameters":True},
      "usage":{"include":True}
    }
    record={"model":model,"expected_label":desired,"success":False,"response_received":False}
    try:
        status,result=call("/chat/completions",payload)
        record["http_status"]=status
        record["response_received"]=True
        record["returned_model"]=result.get("model")
        record["provider"]=result.get("provider")
        usage=result.get("usage") or {}
        record["usage"]={k:usage.get(k) for k in ("prompt_tokens","completion_tokens","total_tokens","cost") if k in usage}
        cost=usage.get("cost")
        if isinstance(cost,(float,int)) and 0<=cost<=0.03:known_cost+=cost
        else:known_cost+=0.03
        choices=result.get("choices") or []
        tool_calls=((choices[0].get("message") or {}).get("tool_calls") or []) if choices else []
        record["finish_reason"]=choices[0].get("finish_reason") if choices else None
        record["tool_call_count"]=len(tool_calls)
        if len(tool_calls)==1:
            fn=tool_calls[0].get("function") or {}
            try:args=json.loads(fn.get("arguments","{}"))
            except Exception:args={}
            record["function_name"]=fn.get("name")
            record["returned_label"]=args.get("action_id")
            record["success"]=status==200 and result.get("model")==model and fn.get("name")=="submit_action" and args=={"action_id":desired}
        record["error"]=((result.get("error") or {}).get("message") or "")[:180]
        record["api_request_id"]=result.get("id")
    except Exception as exc:
        record["transport_error_type"]=type(exc).__name__
        record["transport_error"]="Failure in one attempt; no retry"
        known_cost+=0.03
    rows.append(record)
    (DIR/(model.replace("/","__")+".json")).write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps({"model":model,"http_status":record.get("http_status"),"success":record["success"],"reported_cost":record.get("usage",{}).get("cost")}),flush=True)
report={"protocol":"v4.1-neutral-technical-only","generated_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"balance_before":balance_before,"balance_after":safe_balance(),"models":rows,"calls_attempted":len(rows),"one_request_per_model":True,"known_plus_unknown_reservation_usd":known_cost,"all_four_passed":len(rows)==4 and all(x["success"] for x in rows),"scope":"Four neutral technical probes only; no behavioral main cells, no inference claims","note":"Models and provider configurations require further route-specific freeze before main collection."}
OUT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps({"final":"PASS" if report["all_four_passed"] else "PARTIAL_OR_FAIL","count":len(rows),"known_plus_hold_usd":round(known_cost,6),"output":str(OUT)}),flush=True)
