#!/usr/bin/env python3

import os
import time
import json
import argparse
from dataclasses import dataclass
from typing import Optional, Dict, List
from pathlib import Path
import uuid
import sys
from tabulate import tabulate
from datetime import datetime

@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    reasoning_tokens: Optional[int] = None

@dataclass
class APIResponse:
    content: str
    token_usage: TokenUsage
    thinking_time: float = 0.0
    provider: str = "chutes"
    model: str = "deepseek-ai/DeepSeek-R1"

class RequestTracker:
    def __init__(self, session_id: Optional[str] = None, logs_dir: Optional[str | Path] = None):
        self.session_id = session_id or self._get_current_date()
        self.session_start = time.time()
        self.requests: List[Dict] = []
        
        self._logs_dir = Path(logs_dir) if logs_dir else Path("request_logs")
        self._logs_dir.mkdir(exist_ok=True)
        
        # Load existing requests for today
        date_str = self._get_current_date()
        self._log_file = self._logs_dir / f"session_{date_str}.json"
        
        if self._log_file.exists():
            try:
                with open(self._log_file, 'r') as f:
                    data = json.load(f)
                    self.requests = data.get('requests', [])
            except Exception as e:
                print(f"Error loading existing log file: {e}", file=sys.stderr)

    def _get_current_date(self) -> str:
        """Get the current date in YYYY-MM-DD format."""
        return datetime.now().strftime("%Y-%m-%d")

    def track_request(self, response: APIResponse):
        """Track an API request"""
        request_data = {
            "timestamp": time.time(),
            "content": response.content,
            "token_usage": {
                "prompt_tokens": response.token_usage.prompt_tokens,
                "completion_tokens": response.token_usage.completion_tokens,
                "total_tokens": response.token_usage.total_tokens,
                "reasoning_tokens": response.token_usage.reasoning_tokens
            },
            "thinking_time": response.thinking_time,
            "provider": response.provider,
            "model": response.model
        }
        
        self.requests.append(request_data)
        
        # Save to date-specific log file
        date_str = self._get_current_date()
        log_file = self._logs_dir / f"session_{date_str}.json"
        
        try:
            if log_file.exists():
                with open(log_file, 'r') as f:
                    data = json.load(f)
                    if 'requests' not in data:
                        data = {'requests': []}
                    data['requests'].append(request_data)
            else:
                data = {
                    'requests': [request_data],
                    'metadata': {
                        'session_id': date_str,
                        'start_time': time.time()
                    }
                }
            
            with open(log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving to log file: {e}", file=sys.stderr)

    def get_session_summary(self) -> Dict:
        """Get summary statistics for the session"""
        summary = {
            "total_requests": len(self.requests),
            "total_prompt_tokens": sum(r["token_usage"]["prompt_tokens"] for r in self.requests),
            "total_completion_tokens": sum(r["token_usage"]["completion_tokens"] for r in self.requests),
            "total_tokens": sum(r["token_usage"]["total_tokens"] for r in self.requests),
            "total_thinking_time": sum(r["thinking_time"] for r in self.requests),
            "session_duration": time.time() - self.session_start,
            "provider_stats": {
                "chutes": {
                    "requests": 0,
                    "total_tokens": 0,
                    "models": {}
                }
            }
        }
        
        # Calculate provider-specific stats
        for request in self.requests:
            provider_stats = summary["provider_stats"]["chutes"]
            provider_stats["requests"] += 1
            provider_stats["total_tokens"] += request["token_usage"]["total_tokens"]
            
            # Track model usage
            model = request["model"]
            if model not in provider_stats["models"]:
                provider_stats["models"][model] = {
                    "requests": 0,
                    "total_tokens": 0
                }
            
            model_stats = provider_stats["models"][model]
            model_stats["requests"] += 1
            model_stats["total_tokens"] += request["token_usage"]["total_tokens"]
        
        return summary

_GLOBAL_TRACKERS = {}
_DEFAULT_TRACKER = None

def get_request_tracker(session_id: Optional[str] = None, logs_dir: Optional[Path] = None) -> RequestTracker:
    """Get or create a RequestTracker instance for the given session."""
    global _GLOBAL_TRACKERS, _DEFAULT_TRACKER
    
    if session_id is None:
        if _DEFAULT_TRACKER is None:
            _DEFAULT_TRACKER = RequestTracker(session_id=datetime.now().strftime("%Y-%m-%d"), logs_dir=logs_dir)
        return _DEFAULT_TRACKER
    
    if session_id not in _GLOBAL_TRACKERS:
        _GLOBAL_TRACKERS[session_id] = RequestTracker(session_id=session_id, logs_dir=logs_dir)
    
    tracker = _GLOBAL_TRACKERS[session_id]
    _DEFAULT_TRACKER = tracker  # Update default tracker to the most recently used one
    return tracker 