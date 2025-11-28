# 🍽️ MealMind Google ADK

**Multi-agent meal planning system using Google ADK framework**

A production-ready implementation of intelligent meal planning using Google's official Agent Development Kit (ADK).

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-1.19.0-green.svg)](https://pypi.org/project/google-adk/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 Overview

MealMind demonstrates Google ADK's capabilities through a practical meal planning application that:
- ✅ Generates personalized recipes using Gemini AI
- ✅ Respects dietary constraints and allergies
- ✅ Provides nutritional analysis
- ✅ Estimates ingredient costs
- ✅ Creates multi-day meal plans

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         MealMind ADK App            │
│    (google.adk.apps.app.App)        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│      ADK Runner                     │
│  (google.adk.runners.Runner)        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│    Recipe Generator Agent           │
│  (google.adk.agents.LlmAgent)       │
│                                     │
│  Model: Gemini 2.0 Flash            │
│  Tools: 3 ADK tools                 │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│   InMemorySessionService            │
│  (google.adk.sessions)              │
└─────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone repository
git clone https://github.com/UpasanaGhosh/MealMindGoogleADK.git
cd MealMindGoogleADK

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up API key
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

### Run Demo

```bash
python demo_adk.py
```

## 📂 Project Structure

```
MealMindGoogleADK/
├── agents/
│   └── recipe_generator_adk.py    # LlmAgent implementation
├── tools/
│   └── adk_tools.py               # ADK-compliant tools
├── notebooks/
│   └── kaggle_adk_complete.ipynb  # Kaggle notebook demo
├── orchestrator_adk.py            # Runner + App
├── demo_adk.py                    # Demo script
├── requirements.txt               # Dependencies
└── README.md                      # This file
```

## 🔧 Core Components

### 1. **LlmAgent** (`agents/recipe_generator_adk.py`)
- Gemini 2.0 Flash integration
- Custom system prompts
- Tool integration

### 2. **ADK Tools** (`tools/adk_tools.py`)
- `nutrition_lookup_adk()` - Nutritional data
- `get_household_constraints_adk()` - Dietary restrictions
- `estimate_cost_adk()` - Cost estimation

### 3. **Orchestrator** (`orchestrator_adk.py`)
- Runner for agent execution
- InMemorySessionService for state
- App wrapper with event compaction

### 4. **Demo** (`demo_adk.py`)
- Complete meal planning workflow
- Session management
- Error handling

## 💡 Key Features

### Retry Configuration
```python
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)
```
Ensures robust API calls with automatic retry on rate limits.

### Session Management
```python
session_service = InMemorySessionService()
runner = Runner(agent=recipe_agent, session_service=session_service)
```
Maintains conversation state across interactions.

### Event Compaction
```python
app = App(
    agent=recipe_agent,
    events_compaction_config=EventsCompactionConfig(
        enabled=True,
        max_events=1000
    )
)
```
Optimizes memory usage for long-running sessions.

## 📊 Usage Example

```python
from orchestrator_adk import create_adk_orchestrator

# Initialize
orchestrator = create_adk_orchestrator(api_key="your_key")

# Generate meal plan
result = orchestrator.generate_meal_plan(
    household_id="demo_family",
    preferences={"focus": "healthy meals"},
    num_days=3
)

print(result)
```

## 🔬 Google ADK Components Used

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| `LlmAgent` | AI agent with tools | Recipe generation |
| `Gemini` | LLM model | Gemini 2.0 Flash |
| `Runner` | Agent execution | Meal plan orchestration |
| `InMemorySessionService` | State management | Conversation tracking |
| `App` | Production wrapper | Event compaction |
| `ToolContext` | Tool integration | Custom tool functions |

## 📓 Kaggle Notebook

A complete 13-cell Kaggle notebook is included in `notebooks/kaggle_adk_complete.ipynb`:
- Cell-by-cell walkthrough
- Retry configuration
- Single recipe generation
- 3-day meal plan generation
- Session history viewing

## 🎓 Capstone Project

This project demonstrates:
1. **Official Google ADK Integration** - Using `google-adk` v1.19.0
2. **Production-Ready Architecture** - Error handling, retry logic, session management
3. **Real-World Application** - Practical meal planning with constraints
4. **Tool Integration** - Custom tools with ToolContext
5. **Multi-Agent Patterns** - Orchestration and coordination

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with Google ADK** • **Powered by Gemini** • **Production-Ready**
