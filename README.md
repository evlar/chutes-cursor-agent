# Chutes Cursor Agent: Transform Cursor into a Devin-like AI Assistant

This repository provides everything needed to enhance your Cursor or Windsurf IDE with advanced agentic AI capabilities — similar to Devin—leveraging [Chutes.ai](https://chutes.ai)'s powerful model ecosystem. In under a minute, you'll gain:

* Automated planning and self-evolution using DeepSeek's advanced models
* Extended tool usage, including web browsing, search engine queries, and LLM-driven text/image analysis
* Multi-agent collaboration, with DeepSeek-R1 doing the planning, and specialized models for execution

## Prerequisites

Before you begin, you'll need:
1. A [Chutes.ai](https://chutes.ai) account with API access
2. A Bittensor wallet and hotkey (required for [Chutes.ai](https://chutes.ai) authentication)
3. Python 3.10+ installed on your system

If you don't have a [Chutes.ai](https://chutes.ai) account:
1. Visit [chutes.ai](https://chutes.ai) to create an account
2. Create an API key through the website dashboard
   - Or use the CLI: `chutes keys create --name cursor-key`

For experienced users who prefer manual wallet setup:
```bash
pip install bittensor==5.5.1  # Newer versions require Rust
btcli wallet new_coldkey --n_words 24 --wallet.name chutes-user
btcli wallet new_hotkey --wallet.name chutes-user --n_words 24 --wallet.hotkey chutes-user-hotkey
chutes register
```

## Why This Matters

While Devin impressed many with its capabilities, you can achieve similar functionality using [Chutes.ai](https://chutes.ai)'s model ecosystem. By customizing the `.cursorrules` file (or `.windsurfrules` for Windsurf users) and accompanying Python scripts, you'll unlock advanced features inside your IDE using state-of-the-art models.

## Key Highlights

1. Multi-Agent Architecture
   
   The system operates with two specialized agents:
   - **Planner** (DeepSeek-R1): Handles high-level analysis, task breakdown, and strategic planning
   - **Executor**: Implements specific tasks using the most appropriate specialized models

2. Optimized Model Selection
   
   Intelligent model routing based on task type:
   - **Planning & Complex Reasoning**: DeepSeek-R1
   - **Code Generation**: Qwen2.5-Coder-32B-Instruct
   - **Quick Tasks**: FLUX.1-schnell
   - **UI/UX Design**: UI-TARS-72B-DPO

3. Extended Toolset

   Includes:
   
   * Web scraping with Playwright
   * DuckDuckGo search integration
   * LLM-powered analysis with Chutes.ai models:
     - DeepSeek-R1 (Primary reasoning model)
     - Qwen2.5-72B-Instruct (General tasks)
     - Qwen2.5-Coder-32B-Instruct (Code-specific tasks)
     - FLUX.1-schnell (Fast responses)
     - UI-TARS-72B (UI/UX specific tasks)

4. Self-Evolution

   The system maintains a "Lessons" section to continuously improve its performance based on user interactions and corrections.

## Installation

You have two ways to get started:

### Option 1: Using Cookiecutter (Recommended)

```bash
# Install cookiecutter if you haven't
pip install cookiecutter

# Create a new project
cookiecutter gh:evlar/chutes-cursor-agent --checkout multi-agent
```

### Option 2: Manual Setup

Clone this repository:
```bash
git clone https://github.com/evlar/chutes-cursor-agent.git
cd chutes-cursor-agent
```

Then follow the setup instructions below.

## Setup

1. Create Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Configure environment variables:
```bash
cp .env.example.chutes .env

# Edit .env with your API key:
# Required:
# - CHUTES_API_TOKEN: Your Chutes.ai API key (format: cpk_...)
```

3. Install dependencies:
```bash
pip install -r requirements.txt
python -m playwright install chromium  # Required for web scraping features
```

4. Verify Chutes.ai Connection:
```bash
# Test your API key
curl -s https://api.chutes.ai/users/me -H 'authorization: YOUR_API_KEY'
```

## Testing

To ensure everything is working correctly:

1. Activate the virtual environment if not already active:
```bash
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Run the test suite:
```bash
PYTHONPATH=. pytest -v tests/
```

The test suite includes:
- Search engine integration tests
- Web scraper functionality tests
- Chutes.ai model integration tests
- Token tracking and cost analysis tests
- Screenshot verification tests

Note: For screenshot verification features, Playwright browsers will be installed automatically when you first use the feature.

## Usage

1. Copy all Chutes-specific files from this repository to your project folder
2. For Cursor users: The `.cursorrules` file will be automatically loaded
3. For Windsurf users: Use both `.windsurfrules` and `scratchpad.md`

## Multi-Agent Support

This project leverages Chutes.ai's model ecosystem for a powerful multi-agent system:

### Architecture

The system operates with two primary agents:

1. **Planner (DeepSeek-R1)**
   - High-level analysis and strategic planning
   - Task breakdown and success criteria definition
   - Progress evaluation and milestone tracking
   - Invoked via `tools/plan_exec_llm_chutes.py`

2. **Executor (Specialized Models)**
   - Task implementation and code generation
   - Testing and validation
   - Real-time feedback and progress tracking
   - Uses task-appropriate models from the ecosystem

### Workflow

1. **Task Initialization**
   - Planner analyzes requirements and creates task breakdown
   - Success criteria are defined
   - Initial strategy is formulated

2. **Execution Phase**
   - Executor implements tasks using specialized models
   - Continuous progress tracking
   - Real-time feedback loop with Planner

3. **Quality Assurance**
   - Automated testing and validation
   - Performance metrics tracking
   - Lessons learned documentation

## Setup

1. Create Python virtual environment:
```