# Transform your Cursor into a Devin-like AI Assistant with Chutes.ai Integration

This repository provides everything needed to enhance your Cursor or Windsurf IDE with advanced agentic AI capabilities — similar to Devin—leveraging Chutes.ai's powerful model ecosystem. In under a minute, you'll gain:

* Automated planning and self-evolution using DeepSeek's advanced models
* Extended tool usage, including web browsing, search engine queries, and LLM-driven text/image analysis
* Multi-agent collaboration, with DeepSeek-R1 doing the planning, and specialized models for execution

## Why This Matters

While Devin impressed many with its capabilities, you can achieve similar functionality using Chutes.ai's model ecosystem. By customizing the .cursorrules_chutes file and accompanying Python scripts, you'll unlock advanced features inside Cursor using state-of-the-art models.

## Key Highlights

1. Easy Setup
   
   Copy the provided config files into your project folder. Cursor users need the .cursorrules_chutes file. Setup takes about a minute.

2. Optimized Model Selection
   
   The system includes intelligent model selection based on task complexity:
   - Quick Q&A: Uses FLUX.1-schnell for fast, cost-effective responses
   - Technical expertise: Leverages DeepSeek-R1 for specialized knowledge
   - Code generation: Uses Qwen2.5-Coder-32B for optimized programming tasks
   - Complex tasks: Defaults to DeepSeek-R1 or Qwen2.5-72B for advanced reasoning

3. Extended Toolset

   Includes:
   
   * Web scraping (Playwright)
   * Search engine integration (DuckDuckGo)
   * LLM-powered analysis with Chutes.ai models:
     - DeepSeek-R1 (Primary reasoning model)
     - Qwen2.5-72B-Instruct (General tasks)
     - Qwen2.5-Coder-32B-Instruct (Code-specific tasks)
     - FLUX.1-schnell (Fast responses)
     - UI-TARS-72B (UI/UX specific tasks)

4. Self-Evolution

   The system learns from corrections and updates its "lessons learned" in .cursorrules_chutes.

## Usage

1. Copy all Chutes-specific files from this repository to your project folder
2. For Cursor users: The `.cursorrules_chutes` file will be automatically loaded
3. For Windsurf users: Use both `.windsurfrules_chutes` and `scratchpad_chutes.md`

## Multi-Agent Support

This project leverages Chutes.ai's model ecosystem for a powerful multi-agent system:

### Architecture

- **Planner** (powered by DeepSeek-R1): Handles high-level analysis and strategic planning
- **Executor** (powered by specialized models): Implements specific tasks using the most appropriate model

### Key Benefits

1. **Enhanced Task Quality**
   - Strategic planning with DeepSeek-R1's advanced reasoning
   - Specialized execution with task-appropriate models
   - Continuous validation and refinement

2. **Improved Problem Solving**
   - Comprehensive test strategies from the Planner
   - Optimized execution with specialized models
   - Efficient feedback loop between agents

## Setup

1. Create Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Configure environment variables:
```bash
cp .env.example .env

# Edit .env with your API key:
# Required:
# - CHUTES_API_TOKEN: Your Chutes.ai API key for accessing all models
```

3. Install dependencies:
```bash
pip install -r requirements.txt
python -m playwright install chromium
```

## Tools Included

- Web scraping with JavaScript support
- Search engine integration
- LLM-powered text and image analysis
- Process planning and self-reflection capabilities

## Testing

Run the test suite:

```bash
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
PYTHONPATH=. pytest -v tests/
```

The test suite includes:
- Search engine tests
- Web scraper tests
- Chutes.ai model integration tests
- Token tracking and cost analysis tests

## Important Notes

### Chutes.ai Integration
The system uses Chutes.ai to access various AI models:
- Authentication via CHUTES_API_TOKEN
- Automatic model selection based on task requirements
- Cost-effective routing between models

### Model Selection Logic
Sophisticated model selection based on:
1. Task complexity and token length
2. Required expertise (general, coding, UI/UX)
3. Response time requirements
4. Cost optimization

The selection is automatic but can be manually overridden when needed.

### Cost Management
The system includes built-in cost tracking and optimization:
- Automatic usage of cost-effective models for simple tasks
- Detailed token and cost tracking per session
- Model-specific pricing considerations

## License

MIT License 