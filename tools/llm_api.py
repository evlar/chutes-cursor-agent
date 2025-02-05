#!/usr/bin/env python3

import os
import base64
import time
import sys
import argparse
import mimetypes
from pathlib import Path
from typing import Optional
import requests
from dotenv import load_dotenv
from tools.token_tracker import TokenUsage, APIResponse, get_request_tracker

def load_environment():
    """Load environment variables from .env files"""
    env_files = ['.env.local', '.env', '.env.example']
    env_loaded = False
    
    for env_file in env_files:
        env_path = Path('.') / env_file
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            env_loaded = True
    
    if not env_loaded:
        print("Warning: No .env files found. Using system environment variables only.", file=sys.stderr)

def encode_image_file(image_path: str) -> tuple[str, str]:
    """Encode image file to base64 and determine MIME type"""
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = 'image/png'
    
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    return encoded_string, mime_type

def query_llm(prompt: str, model: str = "deepseek-ai/DeepSeek-R1", 
              image_path: Optional[str] = None, temperature: float = 0.7,
              max_tokens: int = 1024) -> Optional[str]:
    """Query Chutes.ai LLM API"""
    
    api_key = os.getenv('CHUTES_API_TOKEN')
    if not api_key:
        raise ValueError("CHUTES_API_TOKEN not found in environment variables")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = [{"role": "user", "content": []}]
    
    # Add text content
    messages[0]["content"].append({
        "type": "text",
        "text": prompt
    })

    # Add image if provided
    if image_path:
        encoded_image, mime_type = encode_image_file(image_path)
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{encoded_image}"
            }
        })

    data = {
        "model": model,
        "messages": messages,
        "stream": False,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        start_time = time.time()
        # Convert model name to API endpoint format
        model_endpoint = model.lower().replace('/', '-')
        api_url = f"https://chutes-{model_endpoint}.chutes.ai/v1/chat/completions"
        
        response = requests.post(
            api_url,
            headers=headers,
            json=data
        )
        response.raise_for_status()
        thinking_time = time.time() - start_time
        
        result = response.json()
        
        # Track token usage
        token_usage = TokenUsage(
            prompt_tokens=result['usage']['prompt_tokens'],
            completion_tokens=result['usage']['completion_tokens'],
            total_tokens=result['usage']['total_tokens']
        )
        
        # Track the request
        api_response = APIResponse(
            content=result['choices'][0]['message']['content'],
            token_usage=token_usage,
            thinking_time=thinking_time,
            provider="chutes",
            model=model
        )
        get_request_tracker().track_request(api_response)
        
        return result['choices'][0]['message']['content']

    except Exception as e:
        print(f"Error querying Chutes.ai: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description='Query Chutes.ai LLM API')
    parser.add_argument('--prompt', type=str, required=True, help='The prompt to send')
    parser.add_argument('--model', type=str, default="deepseek-ai/DeepSeek-R1", 
                       help='The model to use')
    parser.add_argument('--image', type=str, help='Path to an image file to attach')
    parser.add_argument('--temperature', type=float, default=0.7, 
                       help='Temperature for response generation')
    args = parser.parse_args()

    load_environment()
    response = query_llm(args.prompt, args.model, args.image, args.temperature)
    
    if response:
        print(response)
    else:
        print("Failed to get response from Chutes.ai")
        sys.exit(1)

if __name__ == "__main__":
    main() 