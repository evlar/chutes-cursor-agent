#!/usr/bin/env python3

import unittest
import os
from unittest.mock import patch, MagicMock
import io
import requests
from tests.tools_chutes.llm_api_chutes import load_environment, query_llm
from tools.token_tracker import TokenUsage, APIResponse

class TestEnvironmentLoading(unittest.TestCase):
    def setUp(self):
        self.original_env = dict(os.environ)
        for key in ['TEST_VAR']:
            if key in os.environ:
                del os.environ[key]

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch('pathlib.Path.exists')
    @patch('tools.llm_api_chutes.load_dotenv')
    @patch('builtins.open')
    def test_environment_loading_precedence(self, mock_open, mock_load_dotenv, mock_exists):
        mock_exists.return_value = True
        
        mock_file = MagicMock()
        mock_file.__enter__.return_value = io.StringIO('TEST_VAR=value\n')
        mock_open.return_value = mock_file
        
        def load_dotenv_side_effect(dotenv_path, **kwargs):
            if '.env.local' in str(dotenv_path):
                os.environ['TEST_VAR'] = 'local'
            elif '.env' in str(dotenv_path):
                if 'TEST_VAR' not in os.environ:
                    os.environ['TEST_VAR'] = 'default'
            elif '.env.example' in str(dotenv_path):
                if 'TEST_VAR' not in os.environ:
                    os.environ['TEST_VAR'] = 'example'
        mock_load_dotenv.side_effect = load_dotenv_side_effect
        
        load_environment()
        
        self.assertEqual(os.environ.get('TEST_VAR'), 'local')
        
        calls = mock_load_dotenv.call_args_list
        self.assertEqual(len(calls), 3)
        self.assertTrue(str(calls[0][1]['dotenv_path']).endswith('.env.local'))
        self.assertTrue(str(calls[1][1]['dotenv_path']).endswith('.env'))
        self.assertTrue(str(calls[2][1]['dotenv_path']).endswith('.env.example'))

class TestLLMAPI(unittest.TestCase):
    def setUp(self):
        self.mock_response = MagicMock()
        self.mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Test response"
                }
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        self.mock_response.status_code = 200

        self.env_patcher = patch.dict('os.environ', {
            'CHUTES_API_TOKEN': 'test-chutes-token'
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch('requests.post')
    def test_query_llm_basic(self, mock_post):
        mock_post.return_value = self.mock_response
        response = query_llm("Test prompt", model="deepseek-ai/DeepSeek-R1")
        self.assertEqual(response, "Test response")
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertTrue('https://chutes-deepseek-ai-deepseek-r1.chutes.ai/v1/chat/completions' in call_args[0][0])
        self.assertEqual(call_args[1]['headers']['Authorization'], 'Bearer test-chutes-token')

    @patch('requests.post')
    def test_query_llm_with_image(self, mock_post):
        mock_post.return_value = self.mock_response
        response = query_llm("Describe image", model="deepseek-ai/DeepSeek-R1", 
                           image_path="test.jpg")
        self.assertEqual(response, "Test response")
        
        # Verify image was included in request
        call_args = mock_post.call_args
        self.assertIn('messages', call_args[1]['json'])
        messages = call_args[1]['json']['messages']
        self.assertTrue(any('image' in msg.get('content', [{}])[0] 
                          for msg in messages))

    @patch('requests.post')
    def test_query_error_handling(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("Test error")
        response = query_llm("Test prompt")
        self.assertIsNone(response)

    @patch('requests.post')
    def test_invalid_response(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid request"}
        mock_post.return_value = mock_response
        
        response = query_llm("Test prompt")
        self.assertIsNone(response)

if __name__ == '__main__':
    unittest.main() 