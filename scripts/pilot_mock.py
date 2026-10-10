"""Deterministic fake service for offline pilot testing, never network access."""
from __future__ import annotations
from pilot_compatibility import PilotStopped,APIProblem

class MockTransport:
    def __init__(self,plan,overrides=None):
        self.plan=plan
        self.overrides=overrides or {}
        self.calls=[]
        self.balance=0.75

    def request(self,path,body=None):
        self.calls.append((path,body))
        if path=="/key":
            response={"data":{"limit":0.75,"limit_remaining":self.balance,
                              "limit_reset":None,"is_management_key":False}}
            response["data"].update(self.overrides.get("key",{}))
            return response
        if path=="/models":
            response={"data":[{"id":x["id"],
                      "pricing":{"prompt":str(x["input"]/1_000_000),
                                 "completion":str(x["output"]/1_000_000)}}
                     for x in self.plan["models"]]}
            if "models" in self.overrides:return self.overrides["models"]
            return response
        if path=="/chat/completions":
            if "request_error" in self.overrides:
                raise APIProblem(self.overrides["request_error"])
            choice=body["messages"][-1]["content"].split("Operator directive: Select action ")[1][0]
            response={
                "id":"mock-gen-"+str(len(self.calls)),
                "model":body["model"],
                "choices":[{"finish_reason":"stop","message":{"role":"assistant","content":choice}}],
                "usage":{"cost":0.0009,"prompt_tokens":200,
                          "completion_tokens":3,
                          "completion_tokens_details":{"reasoning_tokens":0}}
            }
            response.update(self.overrides.get("completion",{}))
            self.balance-=0.0009
            return response
        raise PilotStopped("UNEXPECTED_MOCK_REQUEST")
