#!/usr/bin/env python3

import unittest
import os
import json
import shutil
from datetime import datetime
from tools.token_tracker import TokenUsage, APIResponse, TokenTracker, get_token_tracker

class TestTokenTracker(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_logs_dir = "test_logs"
        if os.path.exists(self.test_logs_dir):
            shutil.rmtree(self.test_logs_dir)
        os.makedirs(self.test_logs_dir)
        
        self.tracker = TokenTracker("test-session", logs_dir=self.test_logs_dir)

    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.test_logs_dir):
            shutil.rmtree(self.test_logs_dir)

    def test_token_usage_creation(self):
        """Test TokenUsage object creation and properties"""
        usage = TokenUsage(100, 50, 150, None)
        self.assertEqual(usage.prompt_tokens, 100)
        self.assertEqual(usage.completion_tokens, 50)
        self.assertEqual(usage.total_tokens, 150)
        self.assertIsNone(usage.reasoning_tokens)

    def test_api_response_creation(self):
        """Test APIResponse object creation and properties"""
        usage = TokenUsage(100, 50, 150, None)
        response = APIResponse(
            content="Test response",
            token_usage=usage,
            cost=0.1,
            thinking_time=1.0,
            provider="chutes",
            model="deepseek-ai/DeepSeek-R1"
        )
        
        self.assertEqual(response.content, "Test response")
        self.assertEqual(response.token_usage, usage)
        self.assertEqual(response.cost, 0.1)
        self.assertEqual(response.thinking_time, 1.0)
        self.assertEqual(response.provider, "chutes")
        self.assertEqual(response.model, "deepseek-ai/DeepSeek-R1")

    def test_track_request(self):
        """Test tracking individual requests"""
        response = APIResponse(
            content="Test response",
            token_usage=TokenUsage(100, 50, 150, None),
            cost=0.1,
            thinking_time=1.0,
            provider="chutes",
            model="deepseek-ai/DeepSeek-R1"
        )
        
        self.tracker.track_request(response)
        
        # Verify log file exists and contains correct data
        log_files = os.listdir(self.test_logs_dir)
        self.assertEqual(len(log_files), 1)
        
        log_path = os.path.join(self.test_logs_dir, log_files[0])
        with open(log_path, 'r') as f:
            log_data = json.load(f)
            
        self.assertEqual(len(log_data), 1)
        entry = log_data[0]
        self.assertEqual(entry["content"], "Test response")
        self.assertEqual(entry["token_usage"]["prompt_tokens"], 100)
        self.assertEqual(entry["token_usage"]["completion_tokens"], 50)
        self.assertEqual(entry["token_usage"]["total_tokens"], 150)
        self.assertEqual(entry["cost"], 0.1)
        self.assertEqual(entry["provider"], "chutes")
        self.assertEqual(entry["model"], "deepseek-ai/DeepSeek-R1")

    def test_session_summary(self):
        """Test session summary generation with multiple models"""
        responses = [
            APIResponse(
                content="Test 1",
                token_usage=TokenUsage(100, 50, 150, None),
                cost=0.1,
                thinking_time=1.0,
                provider="chutes",
                model="deepseek-ai/DeepSeek-R1"
            ),
            APIResponse(
                content="Test 2",
                token_usage=TokenUsage(200, 100, 300, None),
                cost=0.2,
                thinking_time=2.0,
                provider="chutes",
                model="Qwen/Qwen2.5-72B-Instruct"
            )
        ]
        
        for response in responses:
            self.tracker.track_request(response)
        
        summary = self.tracker.get_session_summary()
        
        # Verify totals
        self.assertEqual(summary["total_requests"], 2)
        self.assertEqual(summary["total_prompt_tokens"], 300)
        self.assertEqual(summary["total_completion_tokens"], 150)
        self.assertEqual(summary["total_tokens"], 450)
        self.assertAlmostEqual(summary["total_cost"], 0.3, places=6)
        self.assertEqual(summary["total_thinking_time"], 3.0)
        
        # Verify provider stats
        self.assertEqual(len(summary["provider_stats"]), 1)  # Only "chutes" provider
        chutes_stats = summary["provider_stats"]["chutes"]
        self.assertEqual(chutes_stats["requests"], 2)
        
        # Verify model stats
        self.assertEqual(len(chutes_stats["models"]), 2)
        self.assertTrue("deepseek-ai/DeepSeek-R1" in chutes_stats["models"])
        self.assertTrue("Qwen/Qwen2.5-72B-Instruct" in chutes_stats["models"])

    def test_global_token_tracker(self):
        """Test global token tracker instance management"""
        # Get initial tracker with specific session ID
        tracker1 = get_token_tracker("test-global-1", logs_dir=self.test_logs_dir)
        self.assertIsNotNone(tracker1)
        
        # Get another tracker without session ID - should be the same instance
        tracker2 = get_token_tracker(logs_dir=self.test_logs_dir)
        self.assertIs(tracker1, tracker2)
        
        # Get tracker with different session ID - should be new instance
        tracker3 = get_token_tracker("test-global-2", logs_dir=self.test_logs_dir)
        self.assertIsNot(tracker1, tracker3)
        self.assertEqual(tracker3.session_id, "test-global-2")
        
        # Get tracker without session ID - should reuse the latest instance
        tracker4 = get_token_tracker(logs_dir=self.test_logs_dir)
        self.assertIs(tracker3, tracker4)

    def test_log_file_rotation(self):
        """Test log file rotation based on date"""
        # Create responses on different dates
        responses = [
            APIResponse(
                content=f"Test {i}",
                token_usage=TokenUsage(100, 50, 150, None),
                cost=0.1,
                thinking_time=1.0,
                provider="chutes",
                model="deepseek-ai/DeepSeek-R1"
            ) for i in range(2)
        ]
        
        # Mock different dates for each response
        dates = [
            datetime(2024, 3, 1),
            datetime(2024, 3, 2)
        ]
        
        for response, date in zip(responses, dates):
            with patch('datetime.datetime') as mock_datetime:
                mock_datetime.now.return_value = date
                self.tracker.track_request(response)
        
        # Verify log files
        log_files = sorted(os.listdir(self.test_logs_dir))
        self.assertEqual(len(log_files), 2)
        self.assertTrue(all(f.endswith('.json') for f in log_files))
        self.assertTrue('2024-03-01' in log_files[0])
        self.assertTrue('2024-03-02' in log_files[1])

if __name__ == '__main__':
    unittest.main() 