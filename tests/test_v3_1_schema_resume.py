"""Offline regression tests for V3.1 Gemini strict-output transport amendments."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path

SCRIPTS=Path(__file__).resolve().parents[1]/"scripts"
sys.path.insert(0,str(SCRIPTS))
from v3_1_economic_design import build
from v3_1_resume_study import GEMINI,compatible_payload,extract_choice,is_good_response

class ResumeSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.choice=next(r for r in build("calibration") if r["mode"]=="delegated")
        cls.control=next(r for r in build("calibration") if r["mode"]!="delegated")
        cls.prices={GEMINI:{"input_per_m":0.3,"output_per_m":2.5}}

    def test_gemini_schema_is_required_and_valid(self):
        p=compatible_payload(self.choice,GEMINI,self.prices,{})
        self.assertEqual(p["max_tokens"],256)
        self.assertTrue(p["provider"]["require_parameters"])
        self.assertFalse(p["provider"]["allow_fallbacks"])
        self.assertNotIn("reasoning",p)
        self.assertEqual(p["response_format"]["type"],"json_schema")
        self.assertEqual(p["response_format"]["json_schema"]["schema"]["properties"]["choice"]["enum"],["A","B"])
        p2=compatible_payload(self.control,GEMINI,self.prices,{})
        self.assertEqual(p2["response_format"]["json_schema"]["schema"]["properties"]["choice"]["enum"],["A","B","T"])

    def test_json_strictly_parsed_and_verbose_outputs_rejected(self):
        def response(content):
            return {"model":GEMINI,"choices":[{"finish_reason":"stop","message":{"content":content}}]}
        self.assertEqual(extract_choice(self.choice,GEMINI,response('{"choice":"A"}')),"A")
        self.assertTrue(is_good_response(self.choice,GEMINI,response('{"choice":"B"}')))
        self.assertIsNone(extract_choice(self.choice,GEMINI,response("The answer is B")))
        self.assertIsNone(extract_choice(self.choice,GEMINI,response('{"choice":"A","explanation":"reason"}')))
        self.assertIsNone(extract_choice(self.choice,GEMINI,response('{"choice":"T"}')))
        self.assertEqual(extract_choice(self.control,GEMINI,response('{"choice":"T"}')),"T")

    def test_non_gemini_remains_one_letter_only(self):
        m="deepseek/deepseek-v3.2"
        response=lambda value:{"model":m,"choices":[{"finish_reason":"stop","message":{"content":value}}]}
        self.assertEqual(extract_choice(self.choice,m,response("B")),"B")
        self.assertIsNone(extract_choice(self.choice,m,response('{"choice":"B"}')))
        self.assertIsNone(extract_choice(self.choice,m,response("Reasoning... B")))

if __name__=="__main__":
    unittest.main()
