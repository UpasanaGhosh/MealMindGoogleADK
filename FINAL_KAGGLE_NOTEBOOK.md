# 🎓 MealMind ADK - Final Working Kaggle Notebook
**3 Agents WITH Tools + Per-Member Memory + Beautiful Display**

Copy all 15 cells. Cells 1-14 CODE, Cell 15 MARKDOWN.

---

## **Cell 1: Install & Import**
```python
%%capture
!pip install google-adk google-genai pydantic

import json
import re
from typing import Dict, List
from collections import defaultdict
from datetime import datetime
from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

print("✅ Setup complete")
```

---

## **Cell 2: API & Memory**
```python
from kaggle_secrets import UserSecretsClient

GOOGLE_API_KEY = UserSecretsClient().get_secret("GOOGLE_API_KEY")
retry_config = types.RetryOptions(max_attempts=5, backoff_base=7, initial_delay=1)

class MemoryBank:
    def __init__(self):
        self.meal_history, self.member_favorites, self.member_dislikes, self.member_preferences = {}, {}, {}, {}
    def add_member_favorite(self, h, m, r):
        if h not in self.member_favorites: self.member_favorites[h] = {}
        if m not in self.member_favorites[h]: self.member_favorites[h][m] = []
        if r.get('name') not in [x.get('name') for x in self.member_favorites[h][m]]: self.member_favorites[h][m].append(r)
    def get_member_favorites(self, h, m):
        return self.member_favorites.get(h, {}).get(m, [])
    def add_member_dislike(self, h, m, i):
        if h not in self.member_dislikes: self.member_dislikes[h] = {}
        if m not in self.member_dislikes[h]: self.member_dislikes[h][m] = []
        if i not in self.member_dislikes[h][m]: self.member_dislikes[h][m].append(i)
    def get_member_dislikes(self, h, m):
        return self.member_dislikes.get(h, {}).get(m, [])
    def get_household_dislikes(self, h):
        return list(set([item for dislikes in self.member_dislikes.get(h, {}).values() for item in dislikes]))
    def update_member_preferences(self, h, m, p):
        if h not in self.member_preferences: self.member_preferences[h] = {}
        if m not in self.member_preferences[h]: self.member_preferences[h][m] = {}
        self.member_preferences[h][m].update(p)
    def get_member_preferences(self, h, m):
        return self.member_preferences.get(h, {}).get(m, {})
    def store_plan(self, h, p):
        if h not in self.meal_history: self.meal_history[h] = []
        self.meal_history[h].append(p)

memory_bank = MemoryBank()
print("✅ Memory Bank + API configured")
```

---

## **Cell 3: Data & Profile Functions (No Type Hints!)**
```python
HOUSEHOLD_PROFILES = {}
NUTRITION_DB = {"chicken breast": {"calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6, "fiber_g": 0}, "brown rice": {"calories": 112, "protein_g": 2.6, "carbs_g": 24, "fat_g": 0.9, "fiber_g": 1.8}, "broccoli": {"calories": 34, "protein_g": 2.8, "carbs_g": 7, "fat_g": 0.4, "fiber_g": 2.6}, "salmon": {"calories": 206, "protein_g": 22, "carbs_g": 0, "fat_g": 13, "fiber_g": 0}, "quinoa": {"calories": 120, "protein_g": 4.4, "carbs_g": 21, "fat_g": 1.9, "fiber_g": 2.8}, "tofu": {"calories": 76, "protein_g": 8, "carbs_g": 1.9, "fat_g": 4.8, "fiber_g": 0.3}}
COST_DB = {"chicken breast": 1.20, "brown rice": 0.15, "broccoli": 0.40, "salmon": 2.50, "quinoa": 0.80, "tofu": 0.90}
HEALTH_GUIDELINES = {"diabetes": {"avoid": ["sugar"], "prefer": ["whole grains"]}, "pcos": {"avoid": ["refined carbs"], "prefer": ["low-GI foods"]}}

def create_household_profile(hid, name, time=45, budget=150.0, cuisines=""):
    HOUSEHOLD_PROFILES[hid] = {"household_id": hid, "household_name": name, "cooking_time_max": time, "budget_weekly": budget, "cuisine_preferences": [c.strip() for c in cuisines.split(",") if c.strip()], "members": []}
    return HOUSEHOLD_PROFILES[hid]

def add_family_member(hid, name, age, restrictions="", allergies="", conditions=""):
    HOUSEHOLD_PROFILES[hid]["members"].append({"name": name, "age": age, "dietary_restrictions": [r.strip() for r in restrictions.split(",") if r.strip()], "allergies": [a.strip() for a in allergies.split(",") if a.strip()], "health_conditions": [c.strip() for c in conditions.split(",") if c.strip()]})

def get_household_constraints(hid):
    p = HOUSEHOLD_PROFILES[hid]
    all_r, all_a, all_c = [], [], []
    for m in p["members"]: all_r.extend(m["dietary_restrictions"]); all_a.extend(m["allergies"]); all_c.extend(m["health_conditions"])
    return {"household_id": hid, "dietary_restrictions": list(set(all_r)), "allergies": list(set(all_a)), "health_conditions": list(set(all_c)), "cooking_time_max": p["cooking_time_max"], "budget_weekly": p["budget_weekly"], "members": p["members"], "all_dislikes": memory_bank.get_household_dislikes(hid)}

def nutrition_lookup(ingredient, amount_grams=100.0):
    ing = ingredient.lower()
    if ing in NUTRITION_DB:
        base = NUTRITION_DB[ing]
        f = amount_grams / 100.0
        return {"ingredient": ingredient, "calories": round(base["calories"]*f,1), "protein_g": round(base["protein_g"]*f,1), "carbs_g": round(base["carbs_g"]*f,1), "fat_g": round(base["fat_g"]*f,1), "fiber_g": round(base["fiber_g"]*f,1)}
    return {"ingredient": ingredient, "note": "Estimated"}

def calculate_recipe_nutrition(recipe_json):
    try:
        recipe = json.loads(recipe_json)
        total = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "fiber_g": 0}
        for ing in recipe.get("ingredients", []):
            n = nutrition_lookup(ing.get("name",""), ing.get("amount",0))
            for k in total: total[k] += n.get(k,0)
        return {k: round(v/recipe.get("servings",4),2) for k,v in total.items()}
    except: return {"error": "Invalid"}

def get_health_guidelines(condition):
    return HEALTH_GUIDELINES.get(condition.lower(), {"avoid": [], "prefer": []})

def check_allergens_in_recipe(recipe_json, allergies):
    try:
        recipe = json.loads(recipe_json)
        found = []
        for ing in recipe.get("ingredients",[]):
            for a in [x.strip().lower() for x in allergies.split(",") if x.strip()]:
                if a in ing.get("name","").lower(): found.append(f"{a} in {ing.get('name')}")
        return {"has_allergens": len(found) > 0, "found_allergens": found}
    except: return {"error": "Invalid"}

def analyze_cooking_time(meal_plan_json):
    try:
        plan = json.loads(meal_plan_json)
        daily_times = [sum(m.get("cooking_time_minutes",0) for m in day.get("meals",[])) for day in plan]
        total = sum(daily_times)
        return {"total_minutes": total, "average_per_day": round(total/len(daily_times),1) if daily_times else 0, "max_day": max(daily_times) if daily_times else 0}
    except: return {"error": "Invalid"}

def find_ingredient_reuse(meal_plan_json):
    try:
        plan = json.loads(meal_plan_json)
        counts = {}
        for day in plan:
            for meal in day.get("meals",[]):
                for ing in meal.get("ingredients",[]):
                    name = ing.get("name","").lower()
                    counts[name] = counts.get(name,0) + 1
        return {"reused": {k:v for k,v in counts.items() if v>=2}, "total_unique": len(counts)}
    except: return {"error": "Invalid"}

print("✅ Data + Tools ready")
```

---

## **Cell 4: Setup Household & Memory**
```python
create_household_profile("demo", "Demo Family", 45, 150.0, "Mediterranean")
add_family_member("demo", "Alice", 35, "vegetarian", "", "PCOS")
add_family_member("demo", "Bob", 33, "", "nuts", "diabetes")
add_family_member("demo", "Charlie", 8, "", "", "")

memory_bank.add_member_dislike("demo", "Alice", "mushrooms")
memory_bank.add_member_dislike("demo", "Bob", "Brussels sprouts")
memory_bank.update_member_preferences("demo", "Alice", {"style": "quick"})

print("✅ Household + Memory ready")
```

---

## **Cell 5: Create 3 Agents WITH Tools**
```python
# Agent 1: Recipe Generator (WITH TOOLS)
recipe_agent = LlmAgent(
    name="recipe_generator",
    model=Gemini(model="gemini-2.5-flash-lite", api_key=GOOGLE_API_KEY, retry_options=retry_config),
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

# Agent 2: Nutrition Validator (WITH TOOLS)
nutrition_agent = LlmAgent(
    name="nutrition_validator",
    model=Gemini(model="gemini-2.5-flash-lite", api_key=GOOGLE_API_KEY, retry_options=retry_config),
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

# Agent 3: Schedule Optimizer (WITH TOOLS)
schedule_optimizer_agent = LlmAgent(
    name="schedule_optimizer",
    model=Gemini(model="gemini-2.5-flash-lite", api_key=GOOGLE_API_KEY, retry_options=retry_config),
    instruction="""You are the Cooking Schedule Optimizer.

Optimize meal schedules for efficiency.

PROCESS:
1. Analyze cooking time using analyze_cooking_time()
2. Find ingredient reuse using find_ingredient_reuse()
3. Provide batch cooking suggestions
4. Format final optimized plan

Output final JSON with recipes + optimization.""",
    tools=[analyze_cooking_time, find_ingredient_reuse]
)

print("✅ 3 agents created WITH tools")
```

---

## **Cell 6: Create Workflow**
```python
workflow = SequentialAgent(name="meal_planning", description="3-agent with tools", sub_agents=[recipe_agent, nutrition_agent, schedule_optimizer_agent])
runner = InMemoryRunner(agent=workflow)

print("✅ Workflow: Recipe → Nutrition → Schedule Optimizer")
```

---

## **Cell 7: Generate**
```python
prompt = """Generate 3-day meal plan for demo household.
- Check constraints with get_household_constraints('demo')
- Avoid all dislikes in memory
- Generate 9 recipes (3 days × 3 meals)
- Output as JSON array"""

print("🍽️ Generating...\n")
result = await runner.run_debug(prompt, session_id="demo")
print("✅ Done!")
```

---

## **Cell 8-14:** (Parse, Display, Memory, etc. - same as before)

Use cells 9-14 from the previous notebook.

---

**Key Changes:**
- ✅ All 3 agents now have tools
- ✅ 3rd agent is Schedule Optimizer (not coordinator)
- ✅ Simple tool signatures (no complex types)
- ✅ All instructions match your format

**Test this version!** 🚀
