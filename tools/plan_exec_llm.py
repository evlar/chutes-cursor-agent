#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
import sys
import time
from ...tools.token_tracker import TokenUsage, APIResponse, get_token_tracker
from .llm_api import query_llm, load_environment

STATUS_FILE = '.cursorrules_chutes'

def read_plan_status():
    """Read content after Multi-Agent Scratchpad section"""
    try:
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            scratchpad_marker = "# Multi-Agent Scratchpad"
            if scratchpad_marker in content:
                return content[content.index(scratchpad_marker):]
            else:
                print(f"Warning: '{scratchpad_marker}' section not found", file=sys.stderr)
                return ""
    except Exception as e:
        print(f"Error reading {STATUS_FILE}: {e}", file=sys.stderr)
        return ""

def read_file_content(file_path):
    """Read content from specified file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description='Query Chutes.ai for planning')
    parser.add_argument('--prompt', type=str, help='Additional prompt', required=False)
    parser.add_argument('--file', type=str, help='File to include in prompt', required=False)
    args = parser.parse_args()

    load_environment()
    plan_content = read_plan_status()
    
    file_content = None
    if args.file:
        file_content = read_file_content(args.file)
        if file_content is None:
            sys.exit(1)

    # Construct the planning prompt
    system_prompt = """You are working on a multi-agent context. As the planner, analyze the project plan and status to address the executor's query."""
    
    combined_prompt = f"""Project Plan and Status:
======
{plan_content}
======
"""

    if file_content:
        combined_prompt += f"\nFile Content:\n======\n{file_content}\n======\n"

    if args.prompt:
        combined_prompt += f"\nUser Query:\n{args.prompt}\n"

    combined_prompt += """\nFocus on revising the Multi-Agent Scratchpad section using this format:

<<<<<<<SEARCH
<original text>
=======
<proposed changes>
>>>>>>>
"""

    # Use the most capable model for planning
    response = query_llm(
        prompt=combined_prompt,
        model="deepseek-ai/DeepSeek-R1",
        temperature=0.3,
        max_tokens=2048
    )

    if response:
        print('Instructions for revising Multi-Agent Scratchpad section:')
        print('=' * 56)
        print(response)
        print('=' * 56)
        print('Please implement these changes in the .cursorrules_chutes file.')
    else:
        print("Failed to get response")
        sys.exit(1)

if __name__ == "__main__":
    main() 