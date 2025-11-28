# 🍽️ MealMind Google ADK

**Complete 5-Agent Meal Planning System using Google ADK Framework**

A production-ready multi-agent meal planning system using Google's Agent Development Kit (ADK) with Sequential Workflow pattern.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-1.19.0-green.svg)](https://pypi.org/project/google-adk/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 Overview

MealMind demonstrates Google ADK's Sequential Workflow for families with complex dietary needs:

- ✅ **5 Specialized Agents** working in sequence
- ✅ **12 Custom Tools** for comprehensive meal planning
- ✅ **Allergen Safety** validation (critical)
- ✅ **Health Condition** management (diabetes, PCOS, etc.)
- ✅ **Budget Tracking** with cost estimation
- ✅ **Cooking Time** optimization
- ✅ **Grocery List** with shopping tips

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│              GOOGLE ADK SEQUENTIAL WORKFLOW                       │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────┐
│  1. Profile Manager     │  → Gathers household constraints
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│  2. Recipe Generator    │  → Generates meals with Gemini
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│  3. Nutrition Validator │  → Validates safety & nutrition
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│  4. Schedule Optimizer  │  → Optimizes cooking schedule
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│  5. Grocery Generator   │  → Creates shopping list
└────────────────────────┘
```

---

## 📂 Project Structure

```
MealMindGoogleADK/
├── agents/                              # 5 Specialized Agents
│   ├── __init__.py
│   ├── profile_manager_adk.py           # Agent 1: Profile management
│   ├── recipe_generator_adk.py          # Agent 2: Recipe generation
│   ├── nutrition_compliance_adk.py      # Agent 3: Nutrition validation
│   ├── schedule_optimizer_adk.py        # Agent 4: Schedule optimization
│   └── grocery_agent_adk.py             # Agent 5: Grocery list
│
├── tools/                               # 12 Custom Tools
│   ├── __init__.py
│   ├── nutrition_lookup.py              # Nutrition data & calculation
│   ├── profile_store.py                 # Household profile management
│   ├── cost_estimator.py                # Cost estimation
│   ├── health_guidelines.py             # Health condition rules
│   ├── schedule_tools.py                # Cooking time analysis
│   └── grocery_tools.py                 # Shopping list aggregation
│
├── memory/                              # Session Management
│   └── __init__.py                      # (Handled by ADK InMemoryRunner)
│
├── notebooks/                           # Kaggle Notebooks
│   └── complete_5agent_workflow.ipynb   # 14-cell complete demo
│
├── orchestrator.py                      # Sequential workflow coordinator
├── demo_complete.py                     # Demo script
├── requirements.txt                     # Dependencies
├── .gitignore
└── README.md                            # This file
```

**Matches original MealMind structure!**

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

---

## 🔧 5-Agent System

### Agent 1: Profile Manager
**File:** `agents/profile_manager_adk.py`

**Purpose:** Manages household profiles and constraints

**Tools:**
- `create_household_profile()` - Create household
- `add_family_member()` - Add members with restrictions
- `get_household_constraints()` - Get aggregated constraints

### Agent 2: Recipe Generator
**File:** `agents/recipe_generator_adk.py`

**Purpose:** Generates recipes using Gemini AI

**Tools:**
- `get_household_constraints()` - Check dietary restrictions
- `nutrition_lookup()` - Get ingredient nutrition
- `get_health_guidelines()` - Get health condition rules

### Agent 3: Nutrition Validator
**File:** `agents/nutrition_compliance_adk.py`

**Purpose:** Validates recipes for safety

**Tools:**
- `calculate_recipe_nutrition()` - Calculate nutrition
- `check_allergens_in_recipe()` - Check allergens (CRITICAL)
- `get_health_guidelines()` - Validate compliance

### Agent 4: Schedule Optimizer
**File:** `agents/schedule_optimizer_adk.py`

**Purpose:** Optimizes meal schedule

**Tools:**
- `analyze_cooking_time()` - Analyze time distribution
- `find_ingredient_reuse()` - Find batch cooking opportunities

### Agent 5: Grocery Generator
**File:** `agents/grocery_agent_adk.py`

**Purpose:** Creates shopping list

**Tools:**
- `aggregate_ingredients_for_shopping()` - Aggregate ingredients
- `estimate_ingredient_cost()` - Calculate costs

---

## 💡 Usage

```python
import asyncio
from orchestrator import create_orchestrator
from tools import create_household_profile, add_family_member

async def generate_plan():
    # Setup
    create_household_profile("family_01", "My Family", 45, 150.0)
    add_family_member("family_01", "Parent", 35, "vegetarian", "", "diabetes")
    
    # Generate
    orchestrator = create_orchestrator(api_key="your_key")
    result = await orchestrator.generate_meal_plan("family_01", days=3)
    
    print(result)

asyncio.run(generate_plan())
```

---

## 📓 Kaggle Notebook

**File:** `notebooks/complete_5agent_workflow.ipynb`

14 cells demonstrating complete workflow:
- Setup & configuration
- Tool definitions
- Agent creation
- Sequential workflow
- Demo household
- Meal plan generation

**Ready for Kaggle!**

---

## 🎓 Capstone Features

### ✅ Multi-Agent System
- 5 specialized agents
- Sequential coordination
- Google ADK framework

### ✅ Tool Integration
- 12 custom tools
- Proper ADK format (no ToolContext)
- Organized by functionality

### ✅ Real-World Application
- Family meal planning
- Dietary constraints
- Allergen safety
- Budget management
- Health conditions

### ✅ Production Ready
- Retry configuration
- Error handling
- Modular structure
- Complete documentation

---

## 🔑 Google ADK Patterns

**Sequential Workflow:**
```python
workflow = SequentialAgent(
    name="meal_planning",
    agents=[agent1, agent2, agent3, agent4, agent5]
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

---

## 📝 License

MIT License

---

**Built with Google ADK** • **5-Agent System** • **Production-Ready**
