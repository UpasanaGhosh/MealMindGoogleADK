# 📋 Kaggle Notebook - All 14 Cells (Using Restructured Code)

Copy each cell into Kaggle in order. Cells 1-13 are CODE cells, Cell 14 is MARKDOWN.

---

## **Cell 1: Install Dependencies**
```python
%%capture
!pip install google-adk google-genai pydantic python-dotenv
```

---

## **Cell 2: Import Core Libraries**
```python
import json
import asyncio
from typing import Dict, List
from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

print("✅ Libraries imported successfully!")
```

---

## **Cell 3: Configure API Key & Retry**
```python
from kaggle_secrets import UserSecretsClient

user_secrets = UserSecretsClient()
GOOGLE_API_KEY = user_secrets.get_secret("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY in Kaggle Secrets")

# Configure retry for robustness
retry_config = types.RetryOptions(
    max_attempts=5,
    backoff_base=7,
    initial_delay=1
)

print("✅ API key and retry config set")
```

---

## **Cell 4: Define Databases**
```python
# Household storage
HOUSEHOLD_PROFILES = {}

# Nutrition database
NUTRITION_DB = {
    "chicken breast": {"calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6, "fiber_g": 0},
    "brown rice": {"calories": 112, "protein_g": 2.6, "carbs_g": 24, "fat_g": 0.9, "fiber_g": 1.8},
    "broccoli": {"calories": 34, "protein_g": 2.8, "carbs_g": 7, "fat_g": 0.4, "fiber_g": 2.6},
    "salmon": {"calories": 206, "protein_g": 22, "carbs_g": 0, "fat_g": 13, "fiber_g": 0},
    "quinoa": {"calories": 120, "protein_g": 4.4, "carbs_g": 21, "fat_g": 1.9, "fiber_g": 2.8},
    "tofu": {"calories": 76, "protein_g": 8, "carbs_g": 1.9, "fat_g": 4.8, "fiber_g": 0.3}
}

# Cost database (per 100g)
COST_DB = {
    "chicken breast": 1.20, "brown rice": 0.15, "broccoli": 0.40,
    "salmon": 2.50, "quinoa": 0.80, "tofu": 0.90
}

# Health guidelines
HEALTH_GUIDELINES = {
    "diabetes": {"avoid": ["sugar", "white bread"], "prefer": ["whole grains", "vegetables"]},
    "pcos": {"avoid": ["refined carbs"], "prefer": ["low-GI foods", "vegetables"]}
}

print(f"✅ Databases loaded: {len(NUTRITION_DB)} ingredients, {len(HEALTH_GUIDELINES)} conditions")
```

---

## **Cell 5: Profile Management Tools**
```python
def create_household_profile(household_id: str, household_name: str, cooking_time_max: int = 45, budget_weekly: float = 150.0, cuisine_preferences: str = "") -> Dict:
    """Create household profile."""
    cuisines = [c.strip() for c in cuisine_preferences.split(",") if c.strip()]
    HOUSEHOLD_PROFILES[household_id] = {
        "household_id": household_id, "household_name": household_name,
        "cooking_time_max": cooking_time_max, "budget_weekly": budget_weekly,
        "cuisine_preferences": cuisines, "members": []
    }
    return HOUSEHOLD_PROFILES[household_id]

def add_family_member(household_id: str, name: str, age: int, dietary_restrictions: str = "", allergies: str = "", health_conditions: str = "") -> Dict:
    """Add family member."""
    if household_id not in HOUSEHOLD_PROFILES:
        return {"error": "Household not found"}
    member = {
        "name": name, "age": age,
        "dietary_restrictions": [r.strip() for r in dietary_restrictions.split(",") if r.strip()],
        "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
        "health_conditions": [h.strip() for h in health_conditions.split(",") if h.strip()]
    }
    HOUSEHOLD_PROFILES[household_id]["members"].append(member)
    return member

def get_household_constraints(household_id: str) -> Dict:
    """Get all household constraints."""
    if household_id not in HOUSEHOLD_PROFILES:
        return {"error": "Household not found"}
    profile = HOUSEHOLD_PROFILES[household_id]
    all_restrictions, all_allergies, all_conditions = [], [], []
    for m in profile["members"]:
        all_restrictions.extend(m["dietary_restrictions"])
        all_allergies.extend(m["allergies"])
        all_conditions.extend(m["health_conditions"])
    return {
        "household_id": household_id,
        "dietary_restrictions": list(set(all_restrictions)),
        "allergies": list(set(all_allergies)),
        "health_conditions": list(set(all_conditions)),
        "cooking_time_max": profile["cooking_time_max"],
        "budget_weekly": profile["budget_weekly"],
        "members": profile["members"]
    }

print("✅ Profile tools ready (3 tools)")
```

---

## **Cell 6: Nutrition Tools**
```python
def nutrition_lookup(ingredient: str, amount_grams: float = 100.0) -> Dict:
    """Look up nutrition data."""
    ing = ingredient.lower()
    if ing in NUTRITION_DB:
        base = NUTRITION_DB[ing]
        factor = amount_grams / 100.0
        return {
            "ingredient": ingredient, "amount_grams": amount_grams,
            "calories": round(base["calories"] * factor, 1),
            "protein_g": round(base["protein_g"] * factor, 1),
            "carbs_g": round(base["carbs_g"] * factor, 1),
            "fat_g": round(base["fat_g"] * factor, 1),
            "fiber_g": round(base["fiber_g"] * factor, 1)
        }
    return {"ingredient": ingredient, "note": "Estimated values"}

def calculate_recipe_nutrition(recipe_json: str) -> Dict:
    """Calculate recipe nutrition."""
    try:
        recipe = json.loads(recipe_json)
        total = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "fiber_g": 0}
        for ing in recipe.get("ingredients", []):
            n = nutrition_lookup(ing.get("name", ""), ing.get("amount", 0))
            for k in total:
                total[k] += n.get(k, 0)
        servings = recipe.get("servings", 4)
        return {k: round(v / servings, 2) for k, v in total.items()}
    except:
        return {"error": "Invalid JSON"}

def get_health_guidelines(condition: str) -> Dict:
    """Get health guidelines."""
    return HEALTH_GUIDELINES.get(condition.lower(), {"avoid": [], "prefer": []})

def check_allergens_in_recipe(recipe_json: str, allergies: str) -> Dict:
    """Check for allergens."""
    try:
        recipe = json.loads(recipe_json)
        allergy_list = [a.strip().lower() for a in allergies.split(",") if a.strip()]
        found = []
        for ing in recipe.get("ingredients", []):
            for allergen in allergy_list:
                if allergen in ing.get("name", "").lower():
                    found.append(f"{allergen} in {ing.get('name')}")
        return {"has_allergens": len(found) > 0, "found_allergens": found}
    except:
        return {"error": "Invalid JSON"}

print("✅ Nutrition tools ready (4 tools)")
```

---

## **Cell 7: Cost & Schedule Tools**
```python
def estimate_ingredient_cost(ingredient: str, amount_grams: float) -> Dict:
    """Estimate ingredient cost."""
    ing = ingredient.lower()
    if ing in COST_DB:
        cost = (amount_grams / 100.0) * COST_DB[ing]
        return {"ingredient": ingredient, "total_cost": round(cost, 2)}
    return {"ingredient": ingredient, "total_cost": 0.50, "note": "Estimated"}

def analyze_cooking_time(meal_plan_json: str) -> Dict:
    """Analyze cooking time."""
    try:
        plan = json.loads(meal_plan_json)
        daily_times = [sum(m.get("cooking_time_minutes", 0) for m in day.get("meals", [])) for day in plan]
        total = sum(daily_times)
        return {
            "total_minutes": total,
            "average_per_day": round(total / len(daily_times), 1) if daily_times else 0,
            "max_day": max(daily_times) if daily_times else 0
        }
    except:
        return {"error": "Invalid JSON"}

def find_ingredient_reuse(meal_plan_json: str) -> Dict:
    """Find reused ingredients."""
    try:
        plan = json.loads(meal_plan_json)
        counts = {}
        for day in plan:
            for meal in day.get("meals", []):
                for ing in meal.get("ingredients", []):
                    name = ing.get("name", "").lower()
                    counts[name] = counts.get(name, 0) + 1
        reused = {k: v for k, v in counts.items() if v >= 2}
        return {"reused_ingredients": reused, "reuse_count": len(reused)}
    except:
        return {"error": "Invalid JSON"}

def aggregate_ingredients_for_shopping(meal_plan_json: str) -> Dict:
    """Create shopping list."""
    try:
        plan = json.loads(meal_plan_json)
        aggregated = {}
        for day in plan:
            for meal in day.get("meals", []):
                for ing in meal.get("ingredients", []):
                    name = ing.get("name", "").lower()
                    if name in aggregated:
                        aggregated[name]["total_amount"] += ing.get("amount", 0)
                    else:
                        aggregated[name] = {
                            "name": name.title(),
                            "total_amount": ing.get("amount", 0),
                            "unit": ing.get("unit", "grams")
                        }
        shopping_list, total_cost = [], 0
        for name, data in aggregated.items():
            cost_info = estimate_ingredient_cost(name, data["total_amount"])
            shopping_list.append({
                "name": data["name"],
                "amount": round(data["total_amount"], 1),
                "unit": data["unit"],
                "cost": cost_info["total_cost"]
            })
            total_cost += cost_info["total_cost"]
        return {
            "shopping_list": sorted(shopping_list, key=lambda x: x["name"]),
            "total_items": len(shopping_list),
            "total_cost": round(total_cost, 2)
        }
    except:
        return {"error": "Invalid JSON"}

print("✅ Cost & schedule tools ready (4 tools)")
```

---

## **Cell 8: Create Agent 1 - Profile Manager**
```python
profile_agent = LlmAgent(
    name="profile_manager",
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
    instruction="""You are the Profile Manager for MealMind.
    
Your role: Gather and validate household information.

TOOLS:
- create_household_profile(household_id, household_name, cooking_time_max, budget_weekly, cuisine_preferences)
- add_family_member(household_id, name, age, dietary_restrictions, allergies, health_conditions)
- get_household_constraints(household_id)

Output complete household context for next agent.""",
    tools=[create_household_profile, add_family_member, get_household_constraints]
)

print("✅ Agent 1: Profile Manager created")
```

---

## **Cell 9: Create Agent 2 - Recipe Generator**
```python
recipe_agent = LlmAgent(
    name="recipe_generator",
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
    instruction="""You are the Recipe Generator for MealMind.

Generate meal recipes that satisfy ALL household constraints.

CRITICAL RULES:
1. Check household constraints FIRST using get_household_constraints()
2. NEVER include ingredients matching allergies
3. Respect ALL dietary restrictions (vegetarian = NO meat/fish)
4. Follow health condition guidelines
5. Stay within cooking time limit

Output recipes as JSON array.""",
    tools=[get_household_constraints, nutrition_lookup, get_health_guidelines]
)

print("✅ Agent 2: Recipe Generator created")
```

---

## **Cell 10: Create Agent 3 - Nutrition Validator**
```python
nutrition_agent = LlmAgent(
    name="nutrition_validator",
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
    instruction="""You are the Nutrition Compliance Validator.

Validate recipes for safety and nutrition.

PROCESS:
1. Check allergens (CRITICAL - reject if found)
2. Calculate nutrition per serving
3. Validate health guidelines
4. Approve/reject each recipe

Pass only APPROVED recipes to next agent.""",
    tools=[calculate_recipe_nutrition, check_allergens_in_recipe, get_health_guidelines]
)

print("✅ Agent 3: Nutrition Validator created")
```

---

## **Cell 11: Create Agent 4 & 5 - Schedule Optimizer & Grocery Generator**
```python
# Agent 4: Schedule Optimizer
schedule_agent = LlmAgent(
    name="schedule_optimizer",
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
    instruction="""You optimize meal schedules.

Analyze cooking time. Find ingredient reuse.
Suggest batch cooking. Balance workload across days.""",
    tools=[analyze_cooking_time, find_ingredient_reuse]
)

# Agent 5: Grocery Generator
grocery_agent = LlmAgent(
    name="grocery_generator",
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
    instruction="""You create shopping lists.

Aggregate ingredients. Calculate costs.
Check budget. Provide shopping tips.

This is the FINAL output for user.""",
    tools=[aggregate_ingredients_for_shopping, estimate_ingredient_cost]
)

print("✅ Agent 4: Schedule Optimizer created")
print("✅ Agent 5: Grocery Generator created")
```

---

## **Cell 12: Create Sequential Workflow & Runner**
```python
# Create Sequential workflow with all 5 agents
workflow = SequentialAgent(
    name="meal_planning_workflow",
    description="Complete 5-agent meal planning system",
    agents=[
        profile_agent,      # 1. Get household context
        recipe_agent,       # 2. Generate recipes
        nutrition_agent,    # 3. Validate nutrition
        schedule_agent,     # 4. Optimize schedule
        grocery_agent       # 5. Create grocery list
    ]
)

# Create runner
runner = InMemoryRunner(agent=workflow)

print("✅ Sequential workflow ready!")
print("   Pipeline: Profile → Recipe → Nutrition → Schedule → Grocery")
```

---

## **Cell 13: Setup Demo Household**
```python
# Create household
create_household_profile(
    "demo_family",
    "Demo Family",
    cooking_time_max=45,
    budget_weekly=150.0,
    cuisine_preferences="Mediterranean, Indian"
)

# Add family members
add_family_member("demo_family", "Alice", 35, "vegetarian", "", "PCOS")
add_family_member("demo_family", "Bob", 33, "", "nuts", "diabetes")
add_family_member("demo_family", "Charlie", 8, "", "", "")

# Show constraints
constraints = get_household_constraints("demo_family")

print("✅ Demo household created!")
print("\nHousehold Constraints:")
print(json.dumps(constraints, indent=2))
```

---

## **Cell 14: Generate 3-Day Meal Plan**
```python
prompt = """Generate a complete 3-day meal plan for household: demo_family

REQUIREMENTS:
- Alice: vegetarian, PCOS (low-GI foods)
- Bob: nut allergy, diabetes (no sugar)
- Charlie: no restrictions
- Budget: $150/week
- Max 45 min cooking per day

WORKFLOW:
1. Profile Manager: Get constraints
2. Recipe Generator: Generate 9 recipes (3 days × 3 meals)
3. Nutrition Validator: Check allergens & nutrition
4. Schedule Optimizer: Balance cooking time
5. Grocery Generator: Create shopping list

Proceed through all 5 agents."""

print("🍽️ Generating 3-day meal plan...")
print("Processing through 5 agents (this takes 2-3 minutes)...\n")

result = await runner.run_debug(prompt)

print("\n✅ MEAL PLAN GENERATED!")
print("=" * 70)
print(result)
print("=" * 70)
```

---

## **Cell 15: Summary** (MARKDOWN CELL)
```markdown
## 🎉 Complete 5-Agent System Demonstrated!

### Architecture
**Sequential Workflow:** Profile → Recipe → Nutrition → Schedule → Grocery

### 5 Specialized Agents
1. ✅ **Profile Manager** - Household setup
2. ✅ **Recipe Generator** - Meal creation with Gemini
3. ✅ **Nutrition Validator** - Safety checks
4. ✅ **Schedule Optimizer** - Time optimization
5. ✅ **Grocery Generator** - Shopping list

### 12 Custom Tools
- Profile management (3)
- Nutrition analysis (4)
- Cost estimation (2)
- Schedule optimization (2)
- Grocery aggregation (1)

### Google ADK Features
- ✅ Sequential

Agent
- ✅ LlmAgent with Gemini 2.0
- ✅ InMemoryRunner
- ✅ Retry configuration
- ✅ Automatic function calling

### Real-World Application
- ✅ Multi-constraint meal planning
- ✅ Allergen safety (critical)
- ✅ Health condition compliance
- ✅ Budget management
- ✅ Complete grocery list

**GitHub:** MealMindGoogleADK  
**Status:** 🎊 CAPSTONE-READY!
```

---

## ⚠️ IMPORTANT NOTES

1. **Cell Types:**
   - Cells 1-14: **CODE cells**
   - Cell 15: **MARKDOWN cell**

2. **Before Running:**
   - Add `GOOGLE_API_KEY` to Kaggle Secrets
   - Toggle it ON for notebook
   - Run cells in order (1-14)

3. **Expected Runtime:**
   - Cells 1-13: ~30 seconds total
   - Cell 14: ~2-3 minutes (5 agents processing)

**All cells now use the properly restructured modular code!** 🚀
