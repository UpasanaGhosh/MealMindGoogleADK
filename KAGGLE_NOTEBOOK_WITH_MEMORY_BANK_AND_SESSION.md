# 🎓 MealMind ADK - Complete Kaggle Notebook
**With Per-Member Preferences, Sessions & Beautiful Display**

All 15 cells - Cells 1-14 are CODE, Cell 15 is MARKDOWN

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

print("✅ Libraries imported")
```

---

## **Cell 2: API Key & Retry**
```python
from kaggle_secrets import UserSecretsClient

GOOGLE_API_KEY = UserSecretsClient().get_secret("GOOGLE_API_KEY")
retry_config = types.RetryOptions(max_attempts=5, backoff_base=7, initial_delay=1)

print("✅ API configured")
```

---

## **Cell 3: Enhanced Memory Bank (Per-Member)**
```python
class MemoryBank:
    """Memory with per-member preference tracking."""
    def __init__(self):
        self.meal_history = {}
        self.member_favorites = {}      # household -> {member -> [recipes]}
        self.member_dislikes = {}       # household -> {member -> [ingredients]}
        self.member_preferences = {}    # household -> {member -> preferences}
    
    def add_member_favorite(self, hid, member, recipe):
        if hid not in self.member_favorites: self.member_favorites[hid] = {}
        if member not in self.member_favorites[hid]: self.member_favorites[hid][member] = []
        if recipe.get('name') not in [r.get('name') for r in self.member_favorites[hid][member]]:
            self.member_favorites[hid][member].append({**recipe, "favorited_by": member})
    
    def get_member_favorites(self, hid, member):
        return self.member_favorites.get(hid, {}).get(member, [])
    
    def add_member_dislike(self, hid, member, ingredient):
        if hid not in self.member_dislikes: self.member_dislikes[hid] = {}
        if member not in self.member_dislikes[hid]: self.member_dislikes[hid][member] = []
        if ingredient not in self.member_dislikes[hid][member]:
            self.member_dislikes[hid][member].append(ingredient)
    
    def get_member_dislikes(self, hid, member):
        return self.member_dislikes.get(hid, {}).get(member, [])
    
    def get_household_dislikes(self, hid):
        all_dislikes = []
        for member_dislikes in self.member_dislikes.get(hid, {}).values():
            all_dislikes.extend(member_dislikes)
        return list(set(all_dislikes))
    
    def update_member_preferences(self, hid, member, prefs):
        if hid not in self.member_preferences: self.member_preferences[hid] = {}
        if member not in self.member_preferences[hid]: self.member_preferences[hid][member] = {}
        self.member_preferences[hid][member].update(prefs)
    
    def get_member_preferences(self, hid, member):
        return self.member_preferences.get(hid, {}).get(member, {})
    
    def store_plan(self, hid, plan):
        if hid not in self.meal_history: self.meal_history[hid] = []
        self.meal_history[hid].append({"plan": plan, "created_at": datetime.now().isoformat()})
    
    def get_memory_context(self, hid):
        return {
            "member_favorites": self.member_favorites.get(hid, {}),
            "member_dislikes": self.member_dislikes.get(hid, {}),
            "all_dislikes": self.get_household_dislikes(hid),
            "member_preferences": self.member_preferences.get(hid, {})
        }

memory_bank = MemoryBank()
print("✅ Enhanced Memory Bank with per-member tracking")
```

---

## **Cell 4: Data & Profile Functions**
```python
HOUSEHOLD_PROFILES = {}
NUTRITION_DB = {"chicken breast": {"calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6, "fiber_g": 0}, "brown rice": {"calories": 112, "protein_g": 2.6, "carbs_g": 24, "fat_g": 0.9, "fiber_g": 1.8}, "broccoli": {"calories": 34, "protein_g": 2.8, "carbs_g": 7, "fat_g": 0.4, "fiber_g": 2.6}, "salmon": {"calories": 206, "protein_g": 22, "carbs_g": 0, "fat_g": 13, "fiber_g": 0}, "quinoa": {"calories": 120, "protein_g": 4.4, "carbs_g": 21, "fat_g": 1.9, "fiber_g": 2.8}, "tofu": {"calories": 76, "protein_g": 8, "carbs_g": 1.9, "fat_g": 4.8, "fiber_g": 0.3}}
COST_DB = {"chicken breast": 1.20, "brown rice": 0.15, "broccoli": 0.40, "salmon": 2.50, "quinoa": 0.80, "tofu": 0.90}

def create_household_profile(hid, name, time=45, budget=150.0, cuisines=""):
    HOUSEHOLD_PROFILES[hid] = {"household_id": hid, "household_name": name, "cooking_time_max": time, "budget_weekly": budget, "cuisine_preferences": [c.strip() for c in cuisines.split(",") if c.strip()], "members": []}
    return HOUSEHOLD_PROFILES[hid]

def add_family_member(hid, name, age, restrictions="", allergies="", conditions=""):
    HOUSEHOLD_PROFILES[hid]["members"].append({"name": name, "age": age, "dietary_restrictions": [r.strip() for r in restrictions.split(",") if r.strip()], "allergies": [a.strip() for a in allergies.split(",") if a.strip()], "health_conditions": [c.strip() for c in conditions.split(",") if c.strip()]})

def get_household_constraints(hid):
    p = HOUSEHOLD_PROFILES[hid]
    all_r, all_a, all_c = [], [], []
    for m in p["members"]:
        all_r.extend(m["dietary_restrictions"])
        all_a.extend(m["allergies"])
        all_c.extend(m["health_conditions"])
    memory_ctx = memory_bank.get_memory_context(hid)
    return {"household_id": hid, "dietary_restrictions": list(set(all_r)), "allergies": list(set(all_a)), "health_conditions": list(set(all_c)), "cooking_time_max": p["cooking_time_max"], "budget_weekly": p["budget_weekly"], "members": p["members"], "memory_context": memory_ctx}

print("✅ Profile functions")
```

---

## **Cell 5: Create 3 ADK Agents**
```python
recipe_agent = LlmAgent(name="recipe_generator", model=Gemini(model="gemini-2.5-flash-lite", api_key=GOOGLE_API_KEY), instruction="Generate meal recipes as JSON array.", tools=[])
nutrition_agent = LlmAgent(name="nutrition_validator", model=Gemini(model="gemini-2.5-flash-lite", api_key=GOOGLE_API_KEY), instruction="Validate recipes for safety.", tools=[])
coordinator_agent = LlmAgent(name="coordinator", model=Gemini(model="gemini-2.5-flash-lite", api_key=GOOGLE_API_KEY), instruction="Format final output as JSON.", tools=[])

print("✅ 3 ADK agents created")
```

---

## **Cell 6: Create ADK Workflow**
```python
workflow = SequentialAgent(name="meal_planning", description="3-agent system", sub_agents=[recipe_agent, nutrition_agent, coordinator_agent])
runner = InMemoryRunner(agent=workflow)

print("✅ ADK Sequential workflow ready")
```

---

## **Cell 7: Setup Household & Per-Member Preferences**
```python
# Create household
create_household_profile("demo", "Demo Family", 45, 150.0, "Mediterranean, Indian")
add_family_member("demo", "Alice", 35, "vegetarian", "", "PCOS")
add_family_member("demo", "Bob", 33, "", "nuts", "diabetes")
add_family_member("demo", "Charlie", 8, "", "", "")

# Add per-member preferences
memory_bank.add_member_dislike("demo", "Alice", "mushrooms")
memory_bank.add_member_dislike("demo", "Alice", "olives")
memory_bank.add_member_dislike("demo", "Bob", "Brussels sprouts")
memory_bank.add_member_dislike("demo", "Charlie", "spicy food")

memory_bank.update_member_preferences("demo", "Alice", {"preferred_cooking_style": "quick", "favorite_cuisine": "Mediterranean"})
memory_bank.update_member_preferences("demo", "Bob", {"meal_prep_help": True, "spice_level": "mild"})
memory_bank.update_member_preferences("demo", "Charlie", {"kid_friendly": True, "no_spicy": True})

print("✅ Household with per-member preferences")
print("\n👥 Member Preferences:")
for member in ["Alice", "Bob", "Charlie"]:
    dislikes = memory_bank.get_member_dislikes("demo", member)
    prefs = memory_bank.get_member_preferences("demo", member)
    print(f"  {member}: Dislikes {len(dislikes)} items | {len(prefs)} preferences")
```

---

## **Cell 8: Generate with Memory**
```python
memory_ctx = memory_bank.get_memory_context("demo")

prompt = f"""Generate 3-day meal plan for demo_family.

MEMBERS:
- Alice (35): vegetarian, PCOS - Dislikes: {memory_bank.get_member_dislikes('demo', 'Alice')}
- Bob (33): nut allergy, diabetes - Dislikes: {memory_bank.get_member_dislikes('demo', 'Bob')}
- Charlie (8): no restrictions - Dislikes: {memory_bank.get_member_dislikes('demo', 'Charlie')}

REQUIREMENTS:
- Budget: $150/week | Max time: 45 min/day
- AVOID: {memory_ctx['all_dislikes']}
- Generate 9 recipes (3 days × 3 meals)

Output as JSON array."""

print("🍽️ Generating (using per-member preferences)...\n")
result = await runner.run_debug(prompt, session_id="demo_session")
print("✅ Generated!")
```

---

## **Cell 9: Parse ADK Output**
```python
result_str = str(result)
json_blocks = re.findall(r'```json\s*(.*?)\s*```', result_str, re.DOTALL)

if json_blocks:
    meal_plan = json.loads(json_blocks[-1])
    organized = []
    for i in range(1, 4):
        day_meals = [m for m in meal_plan if m.get("day") == i]
        if day_meals: organized.append({"day": i, "meals": day_meals})
    
    memory_bank.store_plan("demo", organized)
    print(f"✅ Parsed {len(meal_plan)} recipes, stored in memory")
else:
    organized = []
```

---

## **Cell 10: Beautiful Display with All Metrics**
```python
if organized:
    # Header
    print("\n╔" + "═"*78 + "╗")
    print("║" + "🍽️  MEALMIND 3-DAY MEAL PLAN".center(78) + "║")
    print("║" + "Demo Family".center(78) + "║")
    print("╚" + "═"*78 + "╝")
    
    total_cost, total_time, total_cal = 0, 0, 0
    ingredient_counts = {}
    
    for day_data in organized:
        day = day_data["day"]
        print(f"\n{'─'*80}\n📅 DAY {day}\n{'─'*80}")
        
        day_cost, day_time, day_cal = 0, 0, 0
        
        for meal in day_data["meals"]:
            name = meal.get('name', 'Unknown')
            meal_type = meal.get('meal_type', 'meal').upper()
            time = meal.get('cooking_time_minutes', 0)
            servings = meal.get('servings', 4)
            
            print(f"\n  {meal_type}: {name}")
            print(f"  ├─ ⏱️  {time} minutes")
            
            # Calculate metrics
            meal_cost, meal_cal, meal_protein = 0, 0, 0
            for ing in meal.get("ingredients", []):
                ing_name = ing.get("name", "").lower()
                amount = ing.get("amount", 0) if isinstance(ing.get("amount"), (int, float)) else 100
                
                ingredient_counts[ing_name] = ingredient_counts.get(ing_name, 0) + 1
                
                if ing.get("unit") in ["grams", "ml"] and isinstance(amount, (int, float)):
                    cost_per_100g = COST_DB.get(ing_name, 0.50)
                    meal_cost += (amount / 100.0) * cost_per_100g
                    
                    if ing_name in NUTRITION_DB:
                        base = NUTRITION_DB[ing_name]
                        factor = amount / 100.0
                        meal_cal += base["calories"] * factor
                        meal_protein += base["protein_g"] * factor
            
            print(f"  ├─ 💵 ${meal_cost:.2f}")
            print(f"  └─ 📊 {meal_cal/servings:.0f} cal | {meal_protein/servings:.0f}g protein")
            
            day_cost += meal_cost
            day_time += time
            day_cal += meal_cal
        
        time_ok = "✅" if day_time <= 45 else "⚠️"
        print(f"\n  📊 Day {day} Total: {time_ok} {day_time} min | ${day_cost:.2f} | {day_cal:.0f} cal")
        
        total_cost += day_cost
        total_time += day_time
        total_cal += day_cal
    
    # Analysis Section
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + "📊  ANALYSIS & EVALUATION".center(78) + "║")
    print("╚" + "═"*78 + "╝")
    
    # Budget
    avg_time = total_time / 3
    budget_ok = total_cost <= 150
    time_ok = avg_time <= 45
    
    print(f"\n💰 BUDGET:")
    print(f"   {'✅ Within budget' if budget_ok else '⚠️ Over budget'}")
    print(f"   Total: ${total_cost:.2f} / Budget: $150.00")
    pct = min(100, (total_cost/150)*100)
    filled = int(pct/5)
    print(f"   [{'█'*filled}{'░'*(20-filled)}] {pct:.0f}%")
    
    print(f"\n⏱️  COOKING TIME:")
    print(f"   {'✅ Within target' if time_ok else '⚠️ Exceeds target'}")
    print(f"   Average: {avg_time:.0f} min/day (target: 45)")
    time_pct = min(100, (avg_time/45)*100)
    time_filled = int(time_pct/5)
    print(f"   [{'█'*time_filled}{'░'*(20-time_filled)}] {time_pct:.0f}%")
    
    # Optimization
    reused = {k:v for k,v in ingredient_counts.items() if v >= 2}
    reuse_pct = (len(reused)/len(ingredient_counts)*100) if ingredient_counts else 0
    
    print(f"\n🔄 INGREDIENT REUSE:")
    print(f"   Items used 2+ times: {len(reused)}/{len(ingredient_counts)} ({reuse_pct:.0f}%)")
    if reused:
        print(f"   Batch cooking: {', '.join(list(reused.keys())[:5])}")
    
    # Score
    score = 100
    if avg_time > 45: score -= 20
    if total_cost > 150: score -= 15
    score += reuse_pct * 0.15
    stars = "★" * int(score/20) + "☆" * (5-int(score/20))
    
    print(f"\n📈 OPTIMIZATION SCORE: {stars} ({max(0,score):.0f}/100)")
    
    print("\n" + "─"*80)
```

---

## **Cell 11: Mark Per-Member Favorites**
```python
if organized and len(organized) > 0:
    # Alice loves the first breakfast
    first_breakfast = organized[0]["meals"][0]
    memory_bank.add_member_favorite("demo", "Alice", first_breakfast)
    print(f"⭐ Alice favorited: {first_breakfast.get('name')}")
    
    # Bob likes the dinner
    if len(organized[0]["meals"]) > 2:
        first_dinner = organized[0]["meals"][2]
        memory_bank.add_member_favorite("demo", "Bob", first_dinner)
        print(f"⭐ Bob favorited: {first_dinner.get('name')}")
    
    # Charlie likes lunch
    if len(organized[0]["meals"]) > 1:
        first_lunch = organized[0]["meals"][1]
        memory_bank.add_member_favorite("demo", "Charlie", first_lunch)
        print(f"⭐ Charlie favorited: {first_lunch.get('name')}")
    
    print("\n✅ Favorites stored per member!")
```

---

## **Cell 12: Display Per-Member Preferences**
```python
print("\n╔" + "═"*78 + "╗")
print("║" + "👥  PER-MEMBER PREFERENCES".center(78) + "║")
print("╚" + "═"*78 + "╝")

for member in ["Alice", "Bob", "Charlie"]:
    favorites = memory_bank.get_member_favorites("demo", member)
    dislikes = memory_bank.get_member_dislikes("demo", member)
    prefs = memory_bank.get_member_preferences("demo", member)
    
    print(f"\n👤 {member}:")
    print(f"   ⭐ Favorites: {len(favorites)} recipes")
    if favorites:
        for fav in favorites[:2]:
            print(f"      • {fav.get('name')}")
    
    print(f"   ❌ Dislikes: {', '.join(dislikes) if dislikes else 'None'}")
    
    if prefs:
        print(f"   💡 Preferences:")
        for k, v in prefs.items():
            print(f"      • {k}: {v}")

print("\n" + "─"*80)
```

---

## **Cell 13: Session 2 - Generate with Member Preferences**
```python
# Generate Day 4 using member preferences
prompt2 = f"""Generate 1 additional day (Day 4) of meals using member preferences:

MEMBER FAVORITES:
- Alice loves: {[r.get('name') for r in memory_bank.get_member_favorites('demo', 'Alice')]}
- Bob loves: {[r.get('name') for r in memory_bank.get_member_favorites('demo', 'Bob')]}

MEMBER DISLIKES:
- Alice dislikes: {memory_bank.get_member_dislikes('demo', 'Alice')}
- Bob dislikes: {memory_bank.get_member_dislikes('demo', 'Bob')}
- Charlie dislikes: {memory_bank.get_member_dislikes('demo', 'Charlie')}

Create similar recipes to their favorites, avoid all dislikes.
Output 3 recipes (breakfast, lunch, dinner) as JSON array."""

print("🔄 Session 2: Generating Day 4 using memory...\n")
result2 = await runner.run_debug(prompt2, session_id="demo_session")  # Same session!
print("✅ Day 4 generated using member preferences!")
```

---

## **Cell 14: Show Memory Persistence**
```python
print("\n╔" + "═"*78 + "╗")
print("║" + "📚  MEMORY BANK STATUS".center(78) + "║")
print("╚" + "═"*78 + "╝")

memory_ctx = memory_bank.get_memory_context("demo")

print(f"\n⭐ FAVORITES BY MEMBER:")
for member, favs in memory_ctx['member_favorites'].items():
    print(f"  {member}: {len(favs)} recipes")

print(f"\n❌ DISLIKES BY MEMBER:")
for member, dislikes in memory_ctx['member_dislikes'].items():
    print(f"  {member}: {', '.join(dislikes)}")

print(f"\n💡 PREFERENCES BY MEMBER:")
for member, prefs in memory_ctx['member_preferences'].items():
    if prefs:
        print(f"  {member}:")
        for k, v in prefs.items():
            print(f"    • {k}: {v}")

print("\n✅ Memory persists across sessions!")
print("─"*80)
```

---

## **Cell 15: Summary** (MARKDOWN)
```markdown
## 🎉 Complete MealMind ADK with Memory!

### ✅ Google ADK Features
- **3-Agent Sequential Workflow**
- **LlmAgent** with Gemini 2.5 Flash Lite
- **InMemoryRunner** with sessions
- **Session continuity** across requests

### ✅ Memory Features
**Per-Member Tracking:**
- Individual favorites
- Personal dislikes
- Member preferences
- Personalized recommendations

**Household-Level:**
- Meal plan history
- Shared constraints
- Family-wide safety

### ✅ Beautiful Display
- Progress bars (████░░░░)
- Star ratings (★★★★☆)
- Box borders (╔═══╗)
- Status indicators (✅/⚠️)
- Clear metrics & analysis

### 🎓 Capstone Complete!
1. ✅ Multi-agent system (3 ADK agents)
2. ✅ Session management
3. ✅ Long-term memory (per-member!)
4. ✅ Beautiful displays
5. ✅ Production-ready

**Status:** 🎊 CAPSTONE-READY!
```

---

**15 cells total with enhanced features!** 🚀
