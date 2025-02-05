#!/usr/bin/env python3

import unittest
import os
from tests.tools_chutes.llm_api_chutes import query_llm, load_environment
import pytest

def requires_chutes(func):
    """Decorator to skip tests if Chutes API token is not available"""
    def wrapper(*args, **kwargs):
        if not os.getenv('CHUTES_API_TOKEN'):
            pytest.skip("CHUTES_API_TOKEN not found in environment")
        return func(*args, **kwargs)
    return wrapper

class TestLLMAPILive(unittest.TestCase):
    def setUp(self):
        self.original_env = dict(os.environ)
        load_environment()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def _test_llm_response(self, model: str, response: str):
        """Helper to test LLM response with common assertions"""
        self.assertIsNotNone(response, f"Response from {model} was None")
        self.assertIsInstance(response, str, f"Response from {model} was not a string")
        self.assertTrue(len(response) > 0, f"Response from {model} was empty")

    @requires_chutes
    def test_deepseek_r1(self):
        """Live test of DeepSeek-R1 model"""
        try:
            response = query_llm("Say 'test'", model="deepseek-ai/DeepSeek-R1")
            self._test_llm_response("DeepSeek-R1", response)
        except Exception as e:
            pytest.skip(f"DeepSeek-R1 API error: {str(e)}")

    @requires_chutes
    def test_qwen_72b(self):
        """Live test of Qwen 72B model"""
        try:
            response = query_llm("Say 'test'", model="Qwen/Qwen2.5-72B-Instruct")
            self._test_llm_response("Qwen-72B", response)
        except Exception as e:
            pytest.skip(f"Qwen-72B API error: {str(e)}")

    @requires_chutes
    def test_qwen_coder(self):
        """Live test of Qwen Coder model"""
        try:
            response = query_llm("Write a Python hello world", 
                               model="Qwen/Qwen2.5-Coder-32B-Instruct")
            self._test_llm_response("Qwen-Coder", response)
        except Exception as e:
            pytest.skip(f"Qwen-Coder API error: {str(e)}")

    @requires_chutes
    def test_llama_70b(self):
        """Live test of Meta Llama model"""
        try:
            response = query_llm("Say 'test'", 
                               model="hugging-quants/Meta-Llama-3-1-70B-Instruct-AWQ-INT4")
            self._test_llm_response("Llama-70B", response)
        except Exception as e:
            pytest.skip(f"Llama-70B API error: {str(e)}")

    @requires_chutes
    def test_flux_schnell(self):
        """Live test of FLUX.1-schnell model"""
        try:
            response = query_llm("Say 'test'", model="FLUX.1-schnell")
            self._test_llm_response("FLUX.1-schnell", response)
        except Exception as e:
            pytest.skip(f"FLUX.1-schnell API error: {str(e)}")

if __name__ == '__main__':
    unittest.main() 