#!/usr/bin/env python3

import os
import pytest
from unittest.mock import patch, MagicMock, mock_open, AsyncMock
from tools.screenshot_utils import take_screenshot_sync, take_screenshot
from tools.llm_api import query_llm
from tools.token_tracker import TokenUsage

class TestScreenshotVerification:
    @pytest.fixture
    def mock_page(self):
        """Mock Playwright page object."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.screenshot = AsyncMock()
        mock_page.set_viewport_size = AsyncMock()
        return mock_page
    
    @pytest.fixture
    def mock_context(self, mock_page):
        """Mock Playwright browser context."""
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        return mock_context
    
    @pytest.fixture
    def mock_browser(self, mock_page):
        """Mock Playwright browser."""
        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()
        return mock_browser
    
    @pytest.fixture
    def mock_playwright(self, mock_browser):
        """Mock Playwright instance."""
        mock_playwright = AsyncMock()
        mock_playwright.chromium = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        return mock_playwright
    
    def test_screenshot_capture(self, mock_playwright, mock_page, tmp_path):
        """Test screenshot capture functionality with mocked Playwright."""
        os.makedirs(tmp_path, exist_ok=True)
        output_path = os.path.join(tmp_path, 'test_screenshot.png')
        
        with open(output_path, 'wb') as f:
            f.write(b'fake_screenshot_data')
        
        with patch('tools.screenshot_utils.async_playwright', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_playwright),
            __aexit__=AsyncMock()
        )):
            actual_path = take_screenshot_sync('http://test.com', output_path)
            
            assert actual_path == output_path
            assert os.path.exists(actual_path)
            with open(actual_path, 'rb') as f:
                assert f.read() == b'fake_screenshot_data'
            
            mock_playwright.chromium.launch.assert_called_once_with(headless=True)
            mock_browser = mock_playwright.chromium.launch.return_value
            mock_browser.new_page.assert_called_once_with(viewport={'width': 1280, 'height': 720})
            mock_page.goto.assert_called_once_with('http://test.com', wait_until='networkidle')
            mock_page.screenshot.assert_called_once_with(path=output_path, full_page=True)
            mock_browser.close.assert_called_once()
    
    def test_llm_verification_chutes(self, tmp_path):
        """Test screenshot verification with Chutes API."""
        screenshot_path = os.path.join(tmp_path, 'test_screenshot.png')
        
        os.makedirs(tmp_path, exist_ok=True)
        with open(screenshot_path, 'wb') as f:
            f.write(b'fake_screenshot_data')
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "The webpage has a blue background and the title is 'agentic.ai test page'"
                }
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        mock_response.status_code = 200
        
        with patch('requests.post', return_value=mock_response):
            response = query_llm(
                "What is the background color of this webpage? What is the title?",
                model="deepseek-ai/DeepSeek-R1",
                image_path=screenshot_path
            )
            
            assert 'blue' in response.lower()
            assert 'agentic.ai test page' in response.lower() 