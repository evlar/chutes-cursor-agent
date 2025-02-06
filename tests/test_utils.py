#!/usr/bin/env python3

import os
import pytest
from tools.llm_api import load_environment

# Load environment at module level
load_environment()

# Example values from .env.example
EXAMPLE_VALUES = {
    'CHUTES_API_TOKEN': 'your_chutes_api_token_here'
}

def get_skip_reason(env_var: str) -> str:
    """Get a descriptive reason why the test was skipped"""
    value = os.getenv(env_var, '').strip()
    if not value:
        return f"{env_var} is not set in environment"
    if value == EXAMPLE_VALUES.get(env_var, ''):
        return f"{env_var} is still set to example value: {value}"
    return f"{env_var} is not properly configured"

def is_unconfigured(env_var: str) -> bool:
    """Check if an environment variable is unset or set to its example value"""
    value = os.getenv(env_var, '').strip()
    return not value or value == EXAMPLE_VALUES.get(env_var, '')

def requires_chutes(func):
    return pytest.mark.skipif(
        is_unconfigured('CHUTES_API_TOKEN'),
        reason=get_skip_reason('CHUTES_API_TOKEN')
    )(func) 