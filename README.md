# 🍽️ MealMind Google ADK

**Complete 3-Agent Meal Planning System using Google ADK Framework**

A production-ready multi-agent meal planning system using Google's Agent Development Kit (ADK) with Sequential Workflow pattern.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-1.19.0-green.svg)](https://pypi.org/project/google-adk/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 Overview

**MealMind is an intelligent multi-agent meal planning assistant that transforms the overwhelming challenge of family meal planning into a manageable, safe, and personalized experience.**

Every week, millions of families face the same struggle: planning meals that satisfy everyone's dietary needs when one child has severe nut allergies, a parent manages diabetes, and another family member follows a vegetarian diet. Traditional meal planning apps serve single users, but real families need solutions that respect **overlapping and conflicting dietary requirements** simultaneously.

MealMind solves this using Google's Agent Development Kit (ADK) with a **3-agent sequential workflow** powered by Gemini AI:

### 🎯 Key Capabilities

- **Generate 7-day meal plans** for entire households (demo shows 3 days)
- **Respect health conditions** - diabetes, PCOS, high blood pressure, and more
- **Handle allergies safely** - critical allergen validation prevents dangerous ingredients
- **Honor preferences** - vegetarian, vegan, dietary restrictions, dislikes
- **Optimize cooking time** - batch prep, ingredient reuse, advance preparation
- **Create grocery lists** - automated shopping lists with cost estimates
- **Learn over time** - memory bank tracks family preferences and favorites
- **Budget-conscious** - stays within household cost constraints

### 💡 Real-World Impact

MealMind helps:
- **Busy parents** reduce decision fatigue and save hours each week
- **Caregivers** manage complex medical diets safely
- **Health-conscious families** maintain dietary goals without stress
- **Multi-generational households** satisfy diverse tastes and needs

### 🤖 Technical Innovation

Built using Google ADK patterns:
- **Multi-agent collaboration** - 3 specialized agents working in sequence
- **Tool integration** - structured functions for household data management
- **Memory systems** - long-term preference storage and session tracking
- **Debug traces** - workflow execution visibility via `run_debug()`
- **Safety-critical validation** - allergen detection and health compliance

**Capstone learning demonstrated:**
- Sequential workflow orchestration with Google ADK
- LLM-driven reasoning with Gemini models
- Retry logic and error handling for production readiness
- Memory persistence for continuous learning

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│              GOOGLE ADK SEQUENTIAL WORKFLOW                       │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────┐
│  1. Recipe Generator    │  → Generates 9 recipes with Gemini
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│  2. Nutrition Validator │  → Validates safety & nutrition
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│  3. Schedule Optimizer  │  → Optimizes cooking schedule
└────────────────────────┘
```

---

## 📂 Project Structure

```
MealMindGoogleADK/
├── agents/                              # 3 Specialized Agents
│   ├── __init__.py
│   ├── recipe_generator_adk.py          # Agent 1: Recipe generation
│   ├── nutrition_validator_adk.py       # Agent 2: Nutrition validation
│   └── schedule_optimizer_adk.py        # Agent 3: Schedule optimization
│
├── tools/                               # Custom Tool Functions
│   ├── __init__.py
│   ├── nutrition_lookup.py              # Nutrition data & calculation
│   ├── profile_store.py                 # Household profile management
│   ├── cost_estimator.py                # Cost estimation
│   ├── health_guidelines.py             # Health condition rules
│   ├── schedule_tools.py                # Cooking time analysis
│   └── grocery_tools.py                 # Shopping list aggregation
│
├── memory/                              # Memory & Session Management
│   ├── __init__.py
│   ├── memory_bank.py                   # Per-member preference storage
│   └── session_manager.py               # Session history tracking
│
├── utils/                               # Utility Functions
│   ├── __init__.py
│   ├── display_utils.py                 # Output formatting
│   └── meal_planning_utils.py           # Helper functions
│
├── notebooks/                           # Demo Notebooks
│   ├── capstone_kaggle_notebook.ipynb   # Original demo
│   └── MEALMIND-FINAL-DEMO.ipynb        # Final demo with docs
│
├── orchestrator.py                      # Sequential workflow coordinator
├── demo_complete.py                     # Demo script
├── requirements.txt                     # Dependencies
├── .gitignore
└── README.md                            # This file
```

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/UpasanaGhosh/MealMindGoogleADK.git
cd MealMindGoogleADK

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

echo "GOOGLE_API_KEY=your_key" > .env
```

### Run Demo

```bash
python demo_complete.py
```

### Run Jupyter Notebook

```bash
jupyter notebook MEALMIND-FINAL-DEMO.ipynb
```

---

## 🔧 3-Agent System

### Agent 1: Recipe Generator
**File:** `agents/recipe_generator_adk.py`

**Purpose:** Generates meal recipes using Gemini AI

**Capabilities:**
- Creates 9 recipes (3 days × 3 meals)
- Considers all household dietary constraints
- Ensures vegetarian compatibility
- Manages allergen avoidance (nuts, dairy, etc.)
- Respects health conditions (diabetes, PCOS)
- Stays within time and budget limits

**Model:** Gemini 2.5 Flash Lite

**Input:** Household constraints from profile

**Output:** JSON array of meal recipes

### Agent 2: Nutrition Validator
**File:** `agents/nutrition_validator_adk.py`

**Purpose:** Validates recipes for safety and nutritional adequacy

**Checks:**
- **Allergen Detection** - Identifies nuts, dairy, gluten, etc.
- **Nutritional Compliance** - Validates against health guidelines
- **Health Conditions** - Ensures diabetes-friendly, PCOS-appropriate meals
- **Safety Critical** - Flags any violations for critical allergies

**Model:** Gemini 2.5 Flash Lite

**Input:** Generated recipes from Recipe Generator

**Output:** Validated recipes with safety notes

### Agent 3: Schedule Optimizer
**File:** `agents/schedule_optimizer_adk.py`

**Purpose:** Optimizes meal preparation schedule

**Optimization:**
- **Time Management** - Ensures total time fits household constraints
- **Batch Cooking** - Identifies prep tasks that can be done together
- **Ingredient Reuse** - Groups recipes sharing ingredients
- **Advance Prep** - Suggests tasks for previous day
- **Final Formatting** - Structures output as actionable JSON

**Model:** Gemini 2.5 Flash Lite

**Input:** Validated recipes from Nutrition Validator

**Output:** Optimized meal plan with schedule

---

## 💡 Usage

### Python Script

```python
import asyncio
from orchestrator import create_orchestrator
from tools import create_household_profile, add_family_member

async def generate_plan():
    # Setup household
    create_household_profile("family_01", "My Family", 45, 150.0)
    add_family_member("family_01", "Parent", 35, "vegetarian", "nuts", "diabetes")
    
    # Generate meal plan
    orchestrator = create_orchestrator(api_key="your_key")
    result = await orchestrator.generate_meal_plan("family_01", days=3)
    
    print(result)

asyncio.run(generate_plan())
```

### Jupyter Notebook

The complete workflow is demonstrated in `MEALMIND-FINAL-DEMO.ipynb` with:
- Comprehensive inline documentation
- Step-by-step explanations
- Interactive execution
- Visual output formatting

---

## 📓 Kaggle Notebook

**File:** `MEALMIND-FINAL-DEMO.ipynb`

23 cells demonstrating complete workflow:
- 📦 Dependency installation and imports
- 🔑 API configuration and memory setup
- 🛠️ Tool and data structure definitions
- 👥 Household profile creation
- 🤖 Agent creation and configuration
- 🔄 Sequential workflow assembly
- ▶️ Meal plan generation
- 📊 Output parsing and organization
- 📋 Display with detailed analysis
- 💾 Memory bank operations
- ✅ Comprehensive summary

**Ready for Kaggle!**

---

## 🎓 Capstone Features

### ✅ Multi-Agent System
- 3 specialized agents with distinct responsibilities
- Sequential coordination pattern
- Google ADK framework implementation
- Clean separation of concerns

### ✅ Real-World Application
- Family meal planning with multiple constraints
- Critical allergen safety (nuts, dairy)
- Health condition management (diabetes, PCOS)
- Budget and time optimization
- Preference learning via memory bank

### ✅ Production Ready
- Retry configuration for API failures
- Error handling and validation
- Modular architecture
- Comprehensive documentation
- Session management
- Memory persistence

---

## 🔑 Google ADK Patterns

**Sequential Workflow:**
```python
workflow = SequentialAgent(
    name="meal_planning",
    sub_agents=[recipe_agent, nutrition_agent, schedule_optimizer_agent]
)
```

**InMemoryRunner:**
```python
runner = InMemoryRunner(agent=workflow)
result = await runner.run_debug(prompt)
```

**Retry Config:**
```python
retry_config = types.RetryOptions(
    max_attempts=5,
    backoff_base=7,
    initial_delay=1
)
```

**Agent Creation:**
```python
agent = LlmAgent(
    name="recipe_generator",
    model=Gemini(model="gemini-2.5-flash-lite", api_key=API_KEY),
    instruction="Generate recipes...",
    tools=[]
)
```

---

## 🔍 Key Features

### Constraint Satisfaction
Successfully handles multiple competing constraints:
- Vegetarian-friendly
- Nut-free (critical allergy)
- Low-GI for PCOS
- Low-carb/sugar for diabetes
- 45-minute time limit
- $150 budget constraint

### Agent Specialization
Each agent focuses on one responsibility:
- **Recipe Generator**: Creativity and meal variety
- **Nutrition Validator**: Safety and compliance
- **Schedule Optimizer**: Efficiency and timing

### Memory & Learning
- Per-member preference tracking
- Session history for context
- Favorite meal storage
- Dietary pattern analysis

---

## 📈 Demo Household

**Demo Configuration:**
```python
Household: "Demo Family"
Budget: $150
Time: 45 minutes

Members:
  - Alice (8): Vegetarian, Allergic to nuts
  - Bob (35): Diabetic, Low-carb
  - Carol (32): PCOS, Low-GI
```

This demonstrates real-world complexity where multiple dietary needs must be satisfied simultaneously.

---

## 🛠️ Development

### Project Dependencies

Key packages:
- `google-genai>=1.19.0` - Google ADK framework
- `python-dotenv` - Environment management
- `jupyter` - Notebook support

### Adding New Agents

1. Create agent file in `agents/` directory
2. Define using `LlmAgent` class
3. Add to workflow sequence in `orchestrator.py`
4. Update documentation

### Adding New Tools

1. Create tool function in `tools/` directory
2. Define input/output schema
3. Register with appropriate agent
4. Add documentation and tests

---

## 📝 License

MIT License

---

## 🎯 Future Enhancements

- [ ] **Observability & Monitoring** - Structured logging, metrics dashboards, trace analysis, and performance monitoring for production deployment
- [ ] Persistent database for meal history
- [ ] User authentication system
- [ ] Web UI for easier interaction
- [ ] Integration with grocery delivery APIs
- [ ] Expanded recipe database
- [ ] Meal rating and feedback system
- [ ] Mobile app development
- [ ] Advanced cost estimation
- [ ] Regional cuisine support
- [ ] Seasonal ingredient optimization

---

**Built with Google ADK** • **3-Agent System** • **Production-Ready** • **Capstone Project**
