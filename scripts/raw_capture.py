"""Capture-first helper for exploratory pilot events.

The raw API envelope and failure category must be saved BEFORE interpreting
a model's text as a scientific choice. Never infer a model choice from HTTP
failures, missing identities or incomplete billing.
"""
from __future__ import annotations
import json
import math
from datetime import datetime, timezone

def cost_from_response(response):
    if not isinstance(response,dict):
        return None
    usage=response.get("usage")
    if not isinstance(usage,dict):
        return None
    cost=usage.get("cost")
    return float(cost) if type(cost) in (int,float) and math.isfinite(cost) and cost>=0 else None

def raw_event(index,model,trial,request_payload,response=None,error=None,reservation=None):
    return {
        "event_type":"api_attempt",
        "index":index,"expected_model":model,
        "trial_id":trial["trial_id"],
        "request_sha256":trial["request_sha256"],
        "request_settings":{k:v for k,v in request_payload.items() if k!="messages"},
        "reservation_usd":reservation,
        "response":response,
        "error":error,
        "recorded_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

def unresolved_trial(model,trial,payload,reason,response=None,status="provider_error"):
    # Exact schema shape, but explicitly NOT a valid model decision.
    if status not in ("provider_error","transport_failure","uninterpretable"):
        raise ValueError("Invalid unresolved-trial status")
    usage=response.get("usage") if isinstance(response,dict) and isinstance(response.get("usage"),dict) else {}
    choices=response.get("choices") if isinstance(response,dict) else None
    first=choices[0] if isinstance(choices,list) and choices and isinstance(choices[0],dict) else {}
    message=first.get("message") if isinstance(first.get("message"),dict) else {}
    raw=message.get("content")
    details=usage.get("completion_tokens_details")
    reasoning=details.get("reasoning_tokens") if isinstance(details,dict) else None
    def tokens(x):
        return x if type(x)==int and x>=0 else None
    provider_response_model=response.get("model") if isinstance(response,dict) else None
    response_id=response.get("id") if isinstance(response,dict) else None
    return {
        "trial_id":trial["trial_id"],"family_id":trial["family_id"],
        "domain":trial["domain"],"frame":trial["frame"],
        "condition":trial["condition"],"directive":trial["directive"],
        "layout":trial["layout"],"mechanism":trial["mechanism"],
        "pairing":trial["pairing"],"q_label":trial["q_label"],
        "n_label":trial["n_label"],"authorized_label":trial["authorized_label"],
        "model_id":model,"provider_route":None,
        "timestamp_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "request_sha256":trial["request_sha256"],
        "settings_json":json.dumps({k:v for k,v in payload.items() if k!="messages"},
                                   sort_keys=True),
        "attempt_status":status,"raw_response":raw if isinstance(raw,str) else None,
        "input_tokens":tokens(usage.get("prompt_tokens")),
        "output_tokens":tokens(usage.get("completion_tokens")),
        "reasoning_tokens":tokens(reasoning),
        "billed_cost_usd":cost_from_response(response),
        "notes":"PILOT RAW-FIRST UNRESOLVED; error="+str(reason)[:150]+
                "; response_id="+str(response_id)[:100]+
                "; returned_model="+str(provider_response_model)[:100],
    }
