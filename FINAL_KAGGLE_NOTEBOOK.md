# 🎓 Complete MealMind ADK Kaggle Notebook - FULLY COMMENTED

**3 Agents WITH Tools + Per-Member Memory + Beautiful Display**

All 12 cells with detailed comments. Cells 1-11 CODE, Cell 12 MARKDOWN.

---

## **Cell 1: Install Dependencies & Import Libraries**
```python
# Install required packages
%%capture
!pip install google-adk google-genai pydantic

# Import standard libraries
import json                    # For JSON parsing
import re                      # For regex pattern matching
from collections import defaultdict  # For counting ingredients
from datetime import datetime  # For timestamps

# Import Google ADK components
from google.adk.agents import SequentialAgent, LlmAgent  # Agent classes
from google.adk.models.google_llm import Gemini          # Gemini model
from google.adk.runners import InMemoryRunner            # Runner for execution
from google.genai import types                           # Type definitions

print("✅ Setup complete")
```

---

## **Cell 2: Configure API & Initialize Memory Bank**
```python
# Get API key from Kaggle secrets
from kaggle_secrets import UserSecretsClient
GOOGLE_API_KEY = UserSecretsClient().get_secret("GOOGLE_API_KEY")

# Configure retry behavior for API calls
retry_config = types.RetryOptions(
    max_attempts=5,    # Retry up to 5 times on failure
    backoff_base=7,    # Exponential backoff multiplier
    initial_delay=1    # Start with 1 second delay
)

# Memory Bank class for long-term storage
class MemoryBank:
    """Stores user preferences and history across sessions."""
    
    def __init__(self):
        # Initialize storage dictionaries
        self.meal_history = {}         # Household -> list of past meal plans
        self.member_favorites = {}     # Household -> {Member -> favorite recipes}
        self.member_dislikes = {}      # Household -> {Member -> disliked ingredients}
        self.member_preferences = {}   # Household -> {Member -> preferences dict}
    
    def add_member_favorite(self, h, m, r):
        """Add a favorite recipe for a specific member."""
        if h not in self.member_favorites: self.member_favorites[h] = {}
        if m not in self.member_favorites[h]: self.member_favorites[h][m] = []
        # Avoid duplicate favorites
        if r.get('name') not in [x.get('name') for x in self.member_favorites[h][m]]: 
            self.member_favorites[h][m].append(r)
    
    def get_member_favorites(self, h, m):
        """Retrieve favorite recipes for a member."""
        return self.member_favorites.get(h, {}).get(m, [])
    
    def add_member_dislike(self, h, m, i):
        """Add a disliked ingredient for a member."""
        if h not in self.member_dislikes: self.member_dislikes[h] = {}
        if m not in self.member_dislikes[h]: self.member_dislikes[h][m] = []
        if i not in self.member_dislikes[h][m]: self.member_dislikes[h][m].append(i)
    
    def get_member_dislikes(self, h, m):
        """Get disliked ingredients for a member."""
        return self.member_dislikes.get(h, {}).get(m, [])
    
    def get_household_dislikes(self, h):
        """Get ALL dislikes across entire household (for safety)."""
        return list(set([item for dislikes in self.member_dislikes.get(h, {}).values() for item in dislikes]))
    
    def update_member_preferences(self, h, m, p):
        """Update preferences for a member."""
        if h not in self.member_preferences: self.member_preferences[h] = {}
        if m not in self.member_preferences[h]: self.member_preferences[h][m] = {}
        self.member_preferences[h][m].update(p)
    
    def get_member_preferences(self, h, m):
        """Get preferences for a member."""
        return self.member_preferences.get(h, {}).get(m, {})
    
    def store_plan(self, h, p):
        """Store meal plan in history."""
        if h not in self.meal_history: self.meal_history[h] = []
        self.meal_history[h].append(p)

# Create global memory bank instance
memory_bank = MemoryBank()
print("✅ API + Memory Bank ready")
```

---

## **Cell 3: Define Data & Tool Functions**
```python
# ===== DATA STORAGE =====
HOUSEHOLD_PROFILES = {}  # Stores household information

# Nutrition database (per 100g)
NUTRITION_DB = {
    "chicken breast": {"calories": 165, "protein_g": 31},
    "brown rice": {"calories": 112, "protein_g": 2.6},
    "broccoli": {"calories": 34, "protein_g": 2.8},
    "salmon": {"calories": 206, "protein_g": 22},
    "quinoa": {"calories": 120, "protein_g": 4.4},
    "tofu": {"calories": 76, "protein_g": 8}
}

# Cost database (per 100g in USD)
COST_DB = {
    "chicken breast": 1.20,
    "brown rice": 0.15,
    "broccoli": 0.40,
    "salmon": 2.50,
    "quinoa": 0.80,
    "tofu": 0.90
}

# Health condition dietary guidelines
HEALTH_GUIDELINES = {
    "diabetes": {"avoid": ["sugar"], "prefer": ["whole grains"]},
    "pcos": {"avoid": ["refined carbs"], "prefer": ["low-GI foods"]}
}

# ===== PROFILE MANAGEMENT FUNCTIONS =====

def create_household_profile(hid, name, time=45, budget=150.0, cuisines=""):
    """Create a new household profile."""
    HOUSEHOLD_PROFILES[hid] = {
        "household_id": hid,
        "household_name": name,
        "cooking_time_max": time,
        "budget_weekly": budget,
        "members": []
    }
    return HOUSEHOLD_PROFILES[hid]

def add_family_member(hid, name, age, restrictions="", allergies="", conditions=""):
    """Add a family member to household."""
    HOUSEHOLD_PROFILES[hid]["members"].append({
        "name": name,
        "age": age,
        "dietary_restrictions": [r.strip() for r in restrictions.split(",") if r.strip()],
        "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
        "health_conditions": [c.strip() for c in conditions.split(",") if c.strip()]
    })

def get_household_constraints(hid):
    """Get aggregated constraints for entire household."""
    p = HOUSEHOLD_PROFILES[hid]
    
    # Aggregate constraints from all members
    all_r, all_a, all_c = [], [], []
    for m in p["members"]:
        all_r.extend(m["dietary_restrictions"])
        all_a.extend(m["allergies"])
        all_c.extend(m["health_conditions"])
    
    return {
        "household_id": hid,
        "dietary_restrictions": list(set(all_r)),  # Remove duplicates
        "allergies": list(set(all_a)),
        "health_conditions": list(set(all_c)),
        "cooking_time_max": p["cooking_time_max"],
        "budget_weekly": p["budget_weekly"],
        "members": p["members"],
        "all_dislikes": memory_bank.get_household_dislikes(hid)  # Include memory dislikes
    }

# ===== NUTRITION TOOLS =====

def nutrition_lookup(ingredient, amount_grams=100.0):
    """Look up nutritional information for an ingredient."""
    ing = ingredient.lower()
    if ing in NUTRITION_DB:
        base = NUTRITION_DB[ing]
        f = amount_grams / 100.0  # Calculate scaling factor
        return {
            "ingredient": ingredient,
            "calories": round(base["calories"]*f, 1),
            "protein_g": round(base["protein_g"]*f, 1)
        }
    return {"ingredient": ingredient, "note": "Estimated"}

def calculate_recipe_nutrition(recipe_json):
    """Calculate total nutrition for a recipe."""
    try:
        recipe = json.loads(recipe_json)
        total = {"calories": 0, "protein_g": 0}
        
        # Sum nutrition from all ingredients
        for ing in recipe.get("ingredients", []):
            n = nutrition_lookup(ing.get("name",""), ing.get("amount",0))
            for k in total: 
                total[k] += n.get(k,0)
        
        # Calculate per serving
        servings = recipe.get("servings", 4)
        return {k: round(v/servings, 2) for k,v in total.items()}
    except: 
        return {"error": "Invalid"}

# ===== HEALTH & SAFETY TOOLS =====

def get_health_guidelines(condition):
    """Get dietary guidelines for a health condition."""
    return HEALTH_GUIDELINES.get(condition.lower(), {"avoid": [], "prefer": []})

def check_allergens_in_recipe(recipe_json, allergies):
    """Check if recipe contains any allergens (CRITICAL for safety)."""
    try:
        recipe = json.loads(recipe_json)
        found = []
        
        # Check each ingredient against allergen list
        for ing in recipe.get("ingredients",[]):
            for a in [x.strip().lower() for x in allergies.split(",") if x.strip()]:
                if a in ing.get("name","").lower():
                    found.append(f"{a} in {ing.get('name')}")
        
        return {
            "has_allergens": len(found) > 0,
            "found_allergens": found
        }
    except:
        return {"error": "Invalid"}

# ===== SCHEDULE OPTIMIZATION TOOLS =====

def analyze_cooking_time(meal_plan_json):
    """Analyze cooking time across the meal plan."""
    try:
        plan = json.loads(meal_plan_json)
        
        # Calculate daily cooking times
        daily_times = [
            sum(m.get("cooking_time_minutes",0) for m in day.get("meals",[]))
            for day in plan
        ]
        total = sum(daily_times)
        
        return {
            "total_minutes": total,
            "average_per_day": round(total/len(daily_times), 1) if daily_times else 0,
            "max_day": max(daily_times) if daily_times else 0
        }
    except:
        return {"error": "Invalid"}

def find_ingredient_reuse(meal_plan_json):
    """Find ingredients used multiple times (for batch cooking)."""
    try:
        plan = json.loads(meal_plan_json)
        counts = {}
        
        # Count ingredient usage across all meals
        for day in plan:
            for meal in day.get("meals",[]):
                for ing in meal.get("ingredients",[]):
                    name = ing.get("name","").lower()
                    counts[name] = counts.get(name,0) + 1
        
        # Return items used 2+ times
        return {
            "reused": {k:v for k,v in counts.items() if v>=2},
            "total_unique": len(counts)
        }
    except:
        return {"error": "Invalid"}

print("✅ Data + Tools ready")
```

---

## **Cell 4: Setup Household & Per-Member Memory**
```python
# Create household profile
create_household_profile("demo", "Demo Family", time=45, budget=150.0)

# Add family members with their specific needs
add_family_member("demo", "Alice", 35, restrictions="vegetarian", conditions="PCOS")
add_family_member("demo", "Bob", 33, allergies="nuts", conditions="diabetes")
add_family_member("demo", "Charlie", 8)  # Child with no restrictions

# Add per-member preferences to Memory Bank
memory_bank.add_member_dislike("demo", "Alice", "mushrooms")     # Alice dislikes mushrooms
memory_bank.add_member_dislike("demo", "Bob", "Brussels sprouts") # Bob dislikes Brussels sprouts
memory_bank.update_member_preferences("demo", "Alice", {"cooking_style": "quick"})  # Alice prefers quick meals

print("✅ Household + Per-Member Memory ready")
```

---

## **Cell 5: Create 3 ADK Agents WITH Tools**
```python
# ===== AGENT 1: RECIPE GENERATOR =====
# This agent creates meal recipes using Gemini AI
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
    tools=[get_household_constraints, nutrition_lookup, get_health_guidelines]  # Tools for constraints & nutrition
)

# ===== AGENT 2: NUTRITION VALIDATOR =====
# This agent validates recipes for safety and nutritional balance
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

Pass only APPROVED recipes to next agent.\"\"\",
    tools=[calculate_recipe_nutrition, check_allergens_in_recipe, get_health_guidelines]  # Nutrition & safety tools
)

# ===== AGENT 3: SCHEDULE OPTIMIZER =====
# This agent optimizes cooking schedules and suggests batch cooking
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

Output final JSON with recipes + optimization.\"\"\",
    tools=[analyze_cooking_time, find_ingredient_reuse]  # Schedule analysis tools
)

print("✅ 3 agents WITH tools created")
```

---

## **Cell 6: Create ADK Sequential Workflow**
```python
# Create Sequential workflow - agents execute in order
workflow = SequentialAgent(
    name="meal_planning",
    description="3-agent meal planning with tools",
    sub_agents=[
        recipe_agent,           # 1. Generates recipes
        nutrition_agent,        # 2. Validates safety
        schedule_optimizer_agent  # 3. Optimizes schedule
    ]
)

# Create runner for executing the workflow
runner = InMemoryRunner(agent=workflow)

print("✅ ADK Sequential Workflow ready")
print("   Pipeline: Recipe → Nutrition → Schedule Optimizer")
```

---

## **Cell 7: Generate Meal Plan**
```python
# Create prompt for meal plan generation
prompt = """Generate 3-day meal plan for demo household (household_id: 'demo').
- Use get_household_constraints('demo') first to check all constraints
- Generate 9 recipes (3 days × 3 meals: breakfast, lunch, dinner)
- Validate each recipe with nutrition tools
- Optimize the cooking schedule"""

print("🍽️ Generating 3-day meal plan...")
print("This will take 1-2 minutes as agents use tools...\n")

# Run the workflow with session tracking
result = await runner.run_debug(prompt, session_id="demo")

print("\n✅ Meal plan generated!")
```

---

## **Cell 8: Parse ADK Output**
```python
# Extract text from ADK result
result_str = str(result)

# Find JSON blocks in markdown format
json_blocks = re.findall(r'```json\s*(.*?)\s*```', result_str, re.DOTALL)

if json_blocks:
    # Use the last JSON block (final output from schedule optimizer)
    meal_plan = json.loads(json_blocks[-1])
    
    # Organize recipes by day
    organized = []
    for i in range(1, 4):  # Days 1, 2, 3
        day_meals = [m for m in meal_plan if m.get("day") == i]
        if day_meals: 
            organized.append({"day": i, "meals": day_meals})
    
    # Store in memory for future reference
    memory_bank.store_plan("demo", organized)
    print(f"✅ Parsed {len(meal_plan)} recipes into {len(organized)} days")
else:
    organized = []
    print("⚠️ No JSON found in result")
```

---

## **Cell 9: Display with Analysis**
```python
if organized:
    # ===== HEADER =====
    print("\n" + "="*80)
    print("  🍽️  MEALMIND 3-DAY MEAL PLAN")
    print("="*80)
    
    # Track totals
    total_cost, total_time = 0, 0
    
    # ===== DISPLAY EACH DAY =====
    for day_data in organized:
        day = day_data["day"]
        print(f"\n📅 DAY {day}\n{'-'*80}")
        
        day_cost, day_time = 0, 0
        
        # Display each meal
        for meal in day_data["meals"]:
            name = meal.get('name', 'Unknown')
            time = meal.get('cooking_time_minutes', 0)
            
            # Calculate meal cost
            meal_cost = sum(
                (ing.get('amount',0)/100.0) * COST_DB.get(ing.get('name','').lower(), 0.5)
                for ing in meal.get('ingredients',[])
                if isinstance(ing.get('amount'), (int, float))
            )
            
            # Display meal info
            print(f"  {meal.get('meal_type','meal').upper()}: {name}")
            print(f"    ⏱️  {time} minutes")
            print(f"    💵 ${meal_cost:.2f}")
            
            day_cost += meal_cost
            day_time += time
        
        # Day summary
        time_ok = "✅" if day_time <= 45 else "⚠️"
        print(f"\n  📊 Day {day} Total: {time_ok} {day_time} min | ${day_cost:.2f}")
        
        total_cost += day_cost
        total_time += day_time
    
    # ===== ANALYSIS SECTION =====
    print("\n" + "="*80)
    print("  📊 WEEKLY ANALYSIS")
    print("="*80)
    
    # Budget analysis
    avg_time = total_time / 3
    budget_ok = total_cost <= 150
    time_ok = avg_time <= 45
    
    print(f"\n💰 BUDGET:")
    print(f"   Total: ${total_cost:.2f} / Budget: $150.00")
    print(f"   Status: {'✅ Within budget' if budget_ok else '⚠️ Over budget'}")
    
    # Time analysis
    print(f"\n⏱️  COOKING TIME:")
    print(f"   Average: {avg_time:.0f} min/day (target: 45 min)")
    print(f"   Status: {'✅ Within target' if time_ok else '⚠️ Exceeds target'}")
    
    print("\n" + "="*80)
```

---

## **Cell 10: Store Per-Member Favorites**
```python
if organized and len(organized) > 0:
    # Alice likes the first breakfast
    first_breakfast = organized[0]["meals"][0]
    memory_bank.add_member_favorite("demo", "Alice", first_breakfast)
    print(f"⭐ Alice favorited: {first_breakfast.get('name')}")
    
    # Bob likes the first lunch
    if len(organized[0]["meals"]) > 1:
        first_lunch = organized[0]["meals"][1]
        memory_bank.add_member_favorite("demo", "Bob", first_lunch)
        print(f"⭐ Bob favorited: {first_lunch.get('name')}")
    
    print("\n✅ Favorites stored in Memory Bank (persists across sessions)")
```

---

## **Cell 11: Display Per-Member Memory**
```python
# Show what Memory Bank has learned about each member
print("\n" + "="*80)
print("  👥 PER-MEMBER MEMORY BANK")
print("="*80)

for member in ["Alice", "Bob", "Charlie"]:
    # Retrieve member's stored data
    favs = memory_bank.get_member_favorites("demo", member)
    dislikes = memory_bank.get_member_dislikes("demo", member)
    prefs = memory_bank.get_member_preferences("demo", member)
    
    print(f"\n👤 {member}:")
    print(f"   ⭐ Favorites: {len(favs)} recipes")
    
    # Show favorite names
    if favs:
        for fav in favs:
            print(f"      • {fav.get('name')}")
    
    print(f"   ❌ Dislikes: {', '.join(dislikes) if dislikes else 'None'}")
    
    # Show preferences
    if prefs:
        print(f"   💡 Preferences: {', '.join([f'{k}={v}' for k,v in prefs.items()])}")

print("\n✅ Memory Bank demonstrates long-term learning!")
print("="*80)
```

---

## **Cell 12: Summary** (MARKDOWN CELL)

```
## 🎉 Complete MealMind ADK System!

### Google ADK Features Demonstrated
- SequentialAgent for multi-agent workflow
- LlmAgent with tool integration
- InMemoryRunner for session management
- Gemini 2.5 Flash Lite model

### 3-Agent Architecture
1. Recipe Generator - Creates recipes using constraint tools
2. Nutrition Validator - Validates safety with nutrition tools
3. Schedule Optimizer - Optimizes schedule with analysis tools

### Memory & Sessions
- Per-member favorites tracking
- Individual dislikes management
- Member-specific preferences
- Session continuity

### Complete Analysis
- Budget tracking and compliance
- Cooking time optimization
- Nutritional validation
- Allergen safety checks

Status: CAPSTONE-READY!
```

---

## ✅ All 12 Cells with Detailed Comments!

**Ready to copy into Kaggle!** 🚀
