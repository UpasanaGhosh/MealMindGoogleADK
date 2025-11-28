# 🍽️ MealMind Google ADK

**Complete 5-Agent Meal Planning System using Google ADK Framework**

A production-ready implementation of intelligent meal planning using Google's official Agent Development Kit (ADK) with Sequential Workflow pattern.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-1.19.0-green.svg)](https://pypi.org/project/google-adk/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 Overview

MealMind demonstrates Google ADK's Sequential Workflow through a practical meal planning application for families with complex dietary needs.

**Key Features:**
- ✅ 5 specialized agents working in sequence
- ✅ 12 custom tools for meal planning
- ✅ Allergen safety validation
- ✅ Health condition management
- ✅ Budget tracking
- ✅ Cooking time optimization
- ✅ Grocery list generation

---

## 🏗️ 5-Agent Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    SEQUENTIAL WORKFLOW                            │
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

## 🔧 Agent Details

### 1. Profile Manager Agent
**Purpose:** Manages household profiles and dietary constraints

**Tools (3):**
- `create_household_profile()` - Create household
- `add_family_member()` - Add members with restrictions
- `get_household_constraints()` - Get aggregated constraints

**Output:** Complete household context for recipe generation

### 2. Recipe Generator Agent
**Purpose:** Generates meal recipes using Gemini AI

**Tools (3):**
- `get_household_constraints()` - Check constraints
- `nutrition_lookup()` - Get ingredient nutrition
- `get_health_guidelines()` - Get health condition rules

**Output:** Array of recipes (3 meals/day × N days)

### 3. Nutrition Validator Agent
**Purpose:** Validates recipes for safety and nutrition

**Tools (3):**
- `calculate_recipe_nutrition()` - Calculate nutrition
- `check_allergens_in_recipe()` - Check allergens (CRITICAL)
- `get_health_guidelines()` - Validate health compliance

**Output:** Approved recipes with nutrition data

### 4. Schedule Optimizer Agent
**Purpose:** Optimizes cooking schedule and efficiency

**Tools (2):**
- `analyze_cooking_time()` - Calculate time stats
- `find_ingredient_reuse()` - Find reusable ingredients

**Output:** Optimized schedule with batch cooking suggestions

### 5. Grocery Generator Agent
**Purpose:** Creates organized shopping list

**Tools (2):**
- `aggregate_ingredients_for_shopping()` - Aggregate ingredients
- `estimate_ingredient_cost()` - Calculate costs

**Output:** Complete grocery list with costs and tips

---

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
python demo_complete_5agents.py
```

---

## 📂 Project Structure

```
MealMindGoogleADK/
├── tools/
│   └── complete_adk_tools.py        # 12 ADK tools
├── agents/
│   └── recipe_generator_adk.py      # Individual agent (legacy)
├── workflow_sequential_adk.py       # 5-agent Sequential workflow
├── demo_complete_5agents.py         # Complete demo script
├── notebooks/
│   └── complete_5agent_workflow.ipynb  # Kaggle notebook (14 cells)
├── requirements.txt
└── README.md
```

---

## 💡 Usage Example

```python
import asyncio
from workflow_sequential_adk import create_meal_planning_runner
from tools.complete_adk_tools import (
    create_household_profile,
    add_family_member
)

async def generate_plan():
    # Setup household
    create_household_profile("family_01", "My Family", 45, 150.0, "Italian, Asian")
    add_family_member("family_01", "Parent", 35, "vegetarian", "", "diabetes")
    add_family_member("family_01", "Child", 8, "", "peanuts", "")
    
    # Create runner
    runner = create_meal_planning_runner(api_key="your_key")
    
    # Generate meal plan
    result = await runner.run_debug(
        "Generate 3-day meal plan for family_01 household"
    )
    
    print(result)

asyncio.run(generate_plan())
```

---

## 📊 Complete Tool Inventory

### Profile Management (3 tools)
- `create_household_profile()` - Initialize household
- `add_family_member()` - Add members
- `get_household_constraints()` - Get constraints

### Nutrition Analysis (4 tools)
- `nutrition_lookup()` - Get nutrition data
- `calculate_recipe_nutrition()` - Calculate recipe nutrition
- `get_health_guidelines()` - Get health condition rules
- `check_allergens_in_recipe()` - Check allergens

### Cost Management (2 tools)
- `estimate_ingredient_cost()` - Estimate costs
- `calculate_meal_plan_cost()` - Calculate total cost

### Schedule Optimization (2 tools)
- `analyze_cooking_time()` - Analyze time
- `find_ingredient_reuse()` - Find reuse opportunities

### Grocery Planning (1 tool)
- `aggregate_ingredients_for_shopping()` - Create shopping list

---

## 📓 Kaggle Notebook

Complete 14-cell notebook in `notebooks/complete_5agent_workflow.ipynb`:

1. Install dependencies
2. Import libraries
3. Configure API key + retry
4. Define data & tools
5. Profile tools
6. Nutrition & cost tools
7. Optimization & grocery tools
8. Collect all tools
9. Create 5 agents
10. Create Sequential workflow
11. Setup demo household
12. Generate 3-day meal plan
13. Display results
14. Summary (markdown)

**Ready to run on Kaggle!**

---

## 🎓 Capstone Demonstration

This project demonstrates:

### 1. Official Google ADK Integration
- Using `google-adk` v1.19.0
- SequentialAgent for workflow coordination
- LlmAgent with Gemini 2.0 Flash
- InMemoryRunner for execution

### 2. Multi-Agent System
- 5 specialized agents
- Sequential workflow pattern
- Agent-to-agent data handoff
- Complete meal planning pipeline

### 3. Tool Integration
- 12 custom tools
- No ToolContext (ADK automatic calling)
- Proper type hints and docstrings
- Error handling

### 4. Production Features
- Retry configuration for API robustness
- Allergen safety checks
- Budget compliance
- Health condition management
- Cooking time optimization

### 5. Real-World Application
- Family meal planning with constraints
- 3-7 day planning capability
- Grocery list generation
- Cost optimization

---

## 🧪 Example Use Case

**Family Setup:**
- **Alice** (35) - Vegetarian, PCOS
- **Bob** (33) - Nut allergy, Diabetes
- **Charlie** (8) - No restrictions
- **Budget:** $150/week
- **Time:** Max 45 min/day cooking

**System Output:**
1. ✅ 3-day meal plan (9 recipes)
2. ✅ All recipes vegetarian-friendly
3. ✅ No nuts in any recipe
4. ✅ PCOS & diabetes guidelines followed
5. ✅ Cooking time optimized
6. ✅ Grocery list under budget

---

## 🔑 Key Google ADK Patterns Used

### Sequential Agent Pattern
```python
workflow = SequentialAgent(
    name="meal_planning",
    agents=[agent1, agent2, agent3, agent4, agent5]
)
```

### LlmAgent with Tools
```python
agent = LlmAgent(
    name="agent_name",
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=config),
    instruction="Clear instructions with tool usage guidelines",
    tools=[tool1, tool2, tool3]
)
```

### InMemoryRunner
```python
runner = InMemoryRunner(agent=workflow)
result = await runner.run_debug(prompt)
```

### Retry Configuration
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

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with Google ADK** • **Powered by Gemini** • **5-Agent System** • **Production-Ready**
