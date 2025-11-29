# 🎓 Complete MealMind ADK Kaggle Notebook - ALL CELLS

**3 Agents WITH Tools + Per-Member Memory + Beautiful Display**

Copy all 12 cells. Cells 1-11 are CODE, Cell 12 is MARKDOWN.

---

## **Cell 1: Install & Import**
```python
%%capture
!pip install google-adk google-genai pydantic

import json
import re
from collections import defaultdict
from datetime import datetime
from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

print("✅ Setup complete")
```

---

## **Cell 2: API Key & Memory Bank**
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
print("✅ API + Memory Bank ready")
```

---

## **Cell 3: Data & Tool Functions**
```python
HOUSEHOLD_PROFILES = {}
NUTRITION_DB = {"chicken breast": {"calories": 165, "protein_g": 31}, "brown rice": {"calories": 112, "protein_g": 2.6}, "broccoli": {"calories": 34, "protein_g": 2.8}, "salmon": {"calories": 206, "protein_g": 22}, "quinoa": {"calories": 120, "protein_g": 4.4}, "tofu": {"calories": 76, "protein_g": 8}}
COST_DB = {"chicken breast": 1.20, "brown rice": 0.15, "broccoli": 0.40, "salmon": 2.50, "quinoa": 0.80, "tofu": 0.90}
HEALTH_GUIDELINES = {"diabetes": {"avoid": ["sugar"], "prefer": ["whole grains"]}, "pcos": {"avoid": ["refined carbs"], "prefer": ["low-GI foods"]}}

def create_household_profile(hid, name, time=45, budget=150.0, cuisines=""):
    HOUSEHOLD_PROFILES[hid] = {"household_id": hid, "household_name": name, "cooking_time_max": time, "budget_weekly": budget, "members": []}
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
        return {"ingredient": ingredient, "calories": round(base["calories"]*f,1), "protein_g": round(base["protein_g"]*f,1)}
    return {"ingredient": ingredient, "note": "Estimated"}

def calculate_recipe_nutrition(recipe_json):
    try:
        recipe = json.loads(recipe_json)
        total = {"calories": 0, "protein_g": 0}
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

## **Cell 4: Setup Household & Per-Member Memory**
```python
create_household_profile("demo", "Demo Family", 45, 150.0)
add_family_member("demo", "Alice", 35, "vegetarian", "", "PCOS")
add_family_member("demo", "Bob", 33, "", "nuts", "diabetes")
add_family_member("demo", "Charlie", 8, "", "", "")

memory_bank.add_member_dislike("demo", "Alice", "mushrooms")
memory_bank.add_member_dislike("demo", "Bob", "Brussels sprouts")
memory_bank.update_member_preferences("demo", "Alice", {"cooking_style": "quick"})

print("✅ Household + Per-Member Memory ready")
```

---

## **Cell 5: Create 3 Agents WITH Tools**
```python
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

print("✅ 3 agents WITH tools created")
```

---

## **Cell 6: Create ADK Sequential Workflow**
```python
workflow = SequentialAgent(
    name="meal_planning",
    description="3-agent with tools",
    sub_agents=[recipe_agent, nutrition_agent, schedule_optimizer_agent]
)

runner = InMemoryRunner(agent=workflow)

print("✅ ADK Sequential Workflow ready")
print("   Recipe → Nutrition → Schedule Optimizer")
```

---

## **Cell 7: Generate Meal Plan**
```python
prompt = """Generate 3-day meal plan for demo household (household_id: 'demo').
- Use get_household_constraints('demo') first
- Generate 9 recipes (3 days × 3 meals)
- Validate with tools
- Optimize schedule"""

print("🍽️ Generating...\n")
result = await runner.run_debug(prompt, session_id="demo")
print("\n✅ Done!")
```

---

## **Cell 8: Parse ADK Output**
```python
result_str = str(result)
json_blocks = re.findall(r'```json\s*(.*?)\s*```', result_str, re.DOTALL)

if json_blocks:
    meal_plan = json.loads(json_blocks[-1])
    organized = []
    for i in range(1,4):
        day_meals = [m for m in meal_plan if m.get("day") == i]
        if day_meals: organized.append({"day": i, "meals": day_meals})
    
    memory_bank.store_plan("demo", organized)
    print(f"✅ Parsed {len(meal_plan)} recipes")
else:
    organized = []
    print("⚠️ No JSON found")
```

---

## **Cell 9: Beautiful Display with Analysis**
```python
if organized:
    print("\n" + "="*80)
    print("  🍽️  MEALMIND 3-DAY MEAL PLAN")
    print("="*80)
    
    total_cost, total_time = 0, 0
    
    for day_data in organized:
        day = day_data["day"]
        print(f"\n📅 DAY {day}\n{'-'*80}")
        
        day_cost, day_time = 0, 0
        for meal in day_data["meals"]:
            name = meal.get('name')
            time = meal.get('cooking_time_minutes', 0)
            meal_cost = sum((ing.get('amount',0)/100.0)*COST_DB.get(ing.get('name','').lower(),0.5) for ing in meal.get('ingredients',[]) if isinstance(ing.get('amount'),(int,float)))
            
            print(f"  {meal.get('meal_type','meal').upper()}: {name}")
            print(f"    ⏱️  {time} min | 💵 ${meal_cost:.2f}")
            
            day_cost += meal_cost
            day_time += time
        
        print(f"\n  Day {day} Total: {day_time} min | ${day_cost:.2f}")
        total_cost += day_cost
        total_time += day_time
    
    # Analysis
    print("\n" + "="*80)
    print("  📊 ANALYSIS")
    print("="*80)
    
    avg_time = total_time / 3
    print(f"\n💰 Budget: ${total_cost:.2f} / $150 ({'✅ OK' if total_cost<=150 else '⚠️ Over'})") 
    print(f"⏱️  Time: {avg_time:.0f} min/day avg ({'✅ OK' if avg_time<=45 else '⚠️ Over'})")
    
    print("\n" + "="*80)
```

---

## **Cell 10: Mark Per-Member Favorites**
```python
if organized:
    memory_bank.add_member_favorite("demo", "Alice", organized[0]["meals"][0])
    print(f"⭐ Alice favorited: {organized[0]['meals'][0].get('name')}")
    
    if len(organized[0]["meals"]) > 1:
        memory_bank.add_member_favorite("demo", "Bob", organized[0]["meals"][1])
        print(f"⭐ Bob favorited: {organized[0]['meals'][1].get('name')}")
    
    print("\n✅ Favorites stored per member!")
```

---

## **Cell 11: Display Per-Member Preferences**
```python
print("\n" + "="*80)
print("  👥 PER-MEMBER PREFERENCES")
print("="*80)

for member in ["Alice", "Bob", "Charlie"]:
    favs = memory_bank.get_member_favorites("demo", member)
    dislikes = memory_bank.get_member_dislikes("demo", member)
    
    print(f"\n👤 {member}:")
    print(f"   ⭐ {len(favs)} favorites")
    print(f"   ❌ Dislikes: {', '.join(dislikes) if dislikes else 'None'}")

print("\n" + "="*80)
```

---

## **Cell 12: Summary** (MARKDOWN CELL)

```
## 🎉 Complete MealMind ADK!

### Google ADK Features
- 3-Agent Sequential Workflow
- LlmAgent with tools
- InMemoryRunner
- Session management

### Memory Features
- Per-member favorites
- Individual dislikes
- Member preferences

### Agents
1. Recipe Generator (with constraint tools)
2. Nutrition Validator (with nutrition tools)
3. Schedule Optimizer (with schedule tools)

Status: CAPSTONE-READY!
```

---

## ✅ Complete!

**12 cells total:**
- Cells 1-11: CODE cells
- Cell 12: MARKDOWN cell

**Features:**
- 3 ADK agents with tools
- Per-member memory tracking
- Session management
- Beautiful display
- Budget & time analysis

**Ready to copy & paste into Kaggle!** 🚀
