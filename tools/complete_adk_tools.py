"""Complete ADK Tools - All tools for 5-agent meal planning system."""
from typing import Dict, List, Any
import json


# ============================================================================
# GLOBAL DATA STORES (In production, use database)
# ============================================================================

HOUSEHOLD_PROFILES = {}

NUTRITION_DB = {
    "chicken breast": {"calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6, "fiber_g": 0},
    "brown rice": {"calories": 112, "protein_g": 2.6, "carbs_g": 24, "fat_g": 0.9, "fiber_g": 1.8},
    "broccoli": {"calories": 34, "protein_g": 2.8, "carbs_g": 7, "fat_g": 0.4, "fiber_g": 2.6},
    "salmon": {"calories": 206, "protein_g": 22, "carbs_g": 0, "fat_g": 13, "fiber_g": 0},
    "quinoa": {"calories": 120, "protein_g": 4.4, "carbs_g": 21, "fat_g": 1.9, "fiber_g": 2.8},
    "spinach": {"calories": 23, "protein_g": 2.9, "carbs_g": 3.6, "fat_g": 0.4, "fiber_g": 2.2},
    "sweet potato": {"calories": 86, "protein_g": 1.6, "carbs_g": 20, "fat_g": 0.1, "fiber_g": 3.0},
    "eggs": {"calories": 155, "protein_g": 13, "carbs_g": 1.1, "fat_g": 11, "fiber_g": 0},
    "olive oil": {"calories": 884, "protein_g": 0, "carbs_g": 0, "fat_g": 100, "fiber_g": 0},
    "tofu": {"calories": 76, "protein_g": 8, "carbs_g": 1.9, "fat_g": 4.8, "fiber_g": 0.3},
}

COST_DB = {
    "chicken breast": 1.20, "brown rice": 0.15, "broccoli": 0.40,
    "salmon": 2.50, "quinoa": 0.80, "spinach": 0.60,
    "sweet potato": 0.30, "eggs": 0.25, "olive oil": 1.00, "tofu": 0.90
}

HEALTH_GUIDELINES = {
    "diabetes": {
        "avoid": ["sugar", "white bread", "white rice", "candy", "soda"],
        "prefer": ["whole grains", "vegetables", "lean protein", "fiber-rich foods"]
    },
    "pcos": {
        "avoid": ["refined carbs", "sugar", "processed foods"],
        "prefer": ["low-GI foods", "vegetables", "lean protein", "healthy fats"]
    },
    "high blood pressure": {
        "avoid": ["high sodium", "processed meats", "canned soups"],
        "prefer": ["fruits", "vegetables", "whole grains", "low-fat dairy"]
    }
}


# ============================================================================
# PROFILE MANAGEMENT TOOLS
# ============================================================================

def create_household_profile(
    household_id: str,
    household_name: str,
    cooking_time_max: int = 45,
    budget_weekly: float = 150.0,
    cuisine_preferences: str = ""
) -> Dict:
    """Create a new household profile.
    
    Args:
        household_id: Unique household identifier
        household_name: Name of the household
        cooking_time_max: Maximum cooking time per day in minutes
        budget_weekly: Weekly grocery budget
        cuisine_preferences: Comma-separated list of preferred cuisines
    
    Returns:
        Created household profile
    """
    cuisines = [c.strip() for c in cuisine_preferences.split(",") if c.strip()]
    
    HOUSEHOLD_PROFILES[household_id] = {
        "household_id": household_id,
        "household_name": household_name,
        "cooking_time_max": cooking_time_max,
        "budget_weekly": budget_weekly,
        "cuisine_preferences": cuisines,
        "members": []
    }
    
    return HOUSEHOLD_PROFILES[household_id]


def add_family_member(
    household_id: str,
    name: str,
    age: int,
    dietary_restrictions: str = "",
    allergies: str = "",
    health_conditions: str = ""
) -> Dict:
    """Add a family member to household.
    
    Args:
        household_id: Household identifier
        name: Member name
        age: Member age
        dietary_restrictions: Comma-separated dietary restrictions
        allergies: Comma-separated allergies
        health_conditions: Comma-separated health conditions
    
    Returns:
        Created member profile
    """
    if household_id not in HOUSEHOLD_PROFILES:
        return {"error": "Household not found"}
    
    member = {
        "name": name,
        "age": age,
        "dietary_restrictions": [r.strip() for r in dietary_restrictions.split(",") if r.strip()],
        "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
        "health_conditions": [h.strip() for h in health_conditions.split(",") if h.strip()]
    }
    
    HOUSEHOLD_PROFILES[household_id]["members"].append(member)
    return member


def get_household_constraints(household_id: str) -> Dict:
    """Get all dietary constraints for a household.
    
    Args:
        household_id: Household identifier
    
    Returns:
        Aggregated constraints from all members
    """
    if household_id not in HOUSEHOLD_PROFILES:
        return {"error": "Household not found"}
    
    profile = HOUSEHOLD_PROFILES[household_id]
    all_restrictions = []
    all_allergies = []
    all_conditions = []
    
    for member in profile["members"]:
        all_restrictions.extend(member["dietary_restrictions"])
        all_allergies.extend(member["allergies"])
        all_conditions.extend(member["health_conditions"])
    
    return {
        "household_id": household_id,
        "dietary_restrictions": list(set(all_restrictions)),
        "allergies": list(set(all_allergies)),
        "health_conditions": list(set(all_conditions)),
        "cooking_time_max": profile["cooking_time_max"],
        "budget_weekly": profile["budget_weekly"],
        "cuisine_preferences": profile["cuisine_preferences"],
        "member_count": len(profile["members"]),
        "members": profile["members"]
    }


# ============================================================================
# NUTRITION TOOLS
# ============================================================================

def nutrition_lookup(ingredient: str, amount_grams: float = 100.0) -> Dict:
    """Look up nutritional information for an ingredient.
    
    Args:
        ingredient: Name of the ingredient
        amount_grams: Amount in grams
    
    Returns:
        Nutritional information dictionary
    """
    ingredient_lower = ingredient.lower()
    
    if ingredient_lower in NUTRITION_DB:
        base = NUTRITION_DB[ingredient_lower]
        factor = amount_grams / 100.0
        return {
            "ingredient": ingredient,
            "amount_grams": amount_grams,
            "calories": round(base["calories"] * factor, 1),
            "protein_g": round(base["protein_g"] * factor, 1),
            "carbs_g": round(base["carbs_g"] * factor, 1),
            "fat_g": round(base["fat_g"] * factor, 1),
            "fiber_g": round(base["fiber_g"] * factor, 1)
        }
    
    # Return estimated values
    return {
        "ingredient": ingredient,
        "amount_grams": amount_grams,
        "calories": 100.0,
        "protein_g": 5.0,
        "carbs_g": 15.0,
        "fat_g": 3.0,
        "fiber_g": 2.0,
        "note": "Estimated values - not in database"
    }


def calculate_recipe_nutrition(recipe_json: str) -> Dict:
    """Calculate total nutrition for a recipe.
    
    Args:
        recipe_json: JSON string of recipe with ingredients
    
    Returns:
        Total nutritional values per serving
    """
    try:
        recipe = json.loads(recipe_json)
    except:
        return {"error": "Invalid recipe JSON"}
    
    total = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "fiber_g": 0}
    
    for ing in recipe.get("ingredients", []):
        amount = ing.get("amount", 0)
        nutrition = nutrition_lookup(ing.get("name", ""), amount)
        
        total["calories"] += nutrition.get("calories", 0)
        total["protein_g"] += nutrition.get("protein_g", 0)
        total["carbs_g"] += nutrition.get("carbs_g", 0)
        total["fat_g"] += nutrition.get("fat_g", 0)
        total["fiber_g"] += nutrition.get("fiber_g", 0)
    
    servings = recipe.get("servings", 4)
    per_serving = {k: round(v / servings, 2) for k, v in total.items()}
    per_serving["servings"] = servings
    
    return per_serving


# ============================================================================
# HEALTH & VALIDATION TOOLS
# ============================================================================

def get_health_guidelines(condition: str) -> Dict:
    """Get dietary guidelines for a health condition.
    
    Args:
        condition: Health condition name
    
    Returns:
        Guidelines with foods to avoid and prefer
    """
    condition_lower = condition.lower()
    return HEALTH_GUIDELINES.get(condition_lower, {
        "avoid": [],
        "prefer": [],
        "note": f"No specific guidelines for {condition}"
    })


def check_allergens_in_recipe(recipe_json: str, allergies: str) -> Dict:
    """Check if recipe contains allergens.
    
    Args:
        recipe_json: JSON string of recipe
        allergies: Comma-separated list of allergies
    
    Returns:
        Dictionary with found allergens
    """
    try:
        recipe = json.loads(recipe_json)
    except:
        return {"error": "Invalid recipe JSON"}
    
    allergy_list = [a.strip().lower() for a in allergies.split(",") if a.strip()]
    found_allergens = []
    
    for ing in recipe.get("ingredients", []):
        ing_name = ing.get("name", "").lower()
        for allergen in allergy_list:
            if allergen in ing_name:
                found_allergens.append(f"{allergen} in {ing.get('name')}")
    
    return {
        "has_allergens": len(found_allergens) > 0,
        "found_allergens": found_allergens
    }


# ============================================================================
# COST ESTIMATION TOOLS
# ============================================================================

def estimate_ingredient_cost(ingredient: str, amount_grams: float) -> Dict:
    """Estimate cost for an ingredient.
    
    Args:
        ingredient: Ingredient name
        amount_grams: Amount in grams
    
    Returns:
        Cost information
    """
    ingredient_lower = ingredient.lower()
    
    if ingredient_lower in COST_DB:
        cost_per_100g = COST_DB[ingredient_lower]
        total_cost = (amount_grams / 100.0) * cost_per_100g
        return {
            "ingredient": ingredient,
            "amount_grams": amount_grams,
            "cost_per_100g": cost_per_100g,
            "total_cost": round(total_cost, 2)
        }
    
    # Estimate for unknown ingredients
    estimated = (amount_grams / 100.0) * 0.50
    return {
        "ingredient": ingredient,
        "amount_grams": amount_grams,
        "total_cost": round(estimated, 2),
        "note": "Estimated cost"
    }


def calculate_meal_plan_cost(meal_plan_json: str) -> Dict:
    """Calculate total cost for a meal plan.
    
    Args:
        meal_plan_json: JSON string of complete meal plan
    
    Returns:
        Cost breakdown
    """
    try:
        plan = json.loads(meal_plan_json)
    except:
        return {"error": "Invalid meal plan JSON"}
    
    total_cost = 0.0
    daily_costs = []
    
    for day in plan:
        day_cost = 0.0
        for meal in day.get("meals", []):
            for ing in meal.get("ingredients", []):
                cost_info = estimate_ingredient_cost(
                    ing.get("name", ""),
                    ing.get("amount", 0)
                )
                day_cost += cost_info["total_cost"]
        
        daily_costs.append(round(day_cost, 2))
        total_cost += day_cost
    
    return {
        "total_cost": round(total_cost, 2),
        "daily_costs": daily_costs,
        "average_per_day": round(total_cost / len(daily_costs), 2) if daily_costs else 0
    }


# ============================================================================
# SCHEDULE OPTIMIZATION TOOLS
# ============================================================================

def analyze_cooking_time(meal_plan_json: str) -> Dict:
    """Analyze cooking times across meal plan.
    
    Args:
        meal_plan_json: JSON string of meal plan
    
    Returns:
        Cooking time statistics
    """
    try:
        plan = json.loads(meal_plan_json)
    except:
        return {"error": "Invalid meal plan JSON"}
    
    daily_times = []
    total_time = 0
    
    for day in plan:
        day_time = sum(meal.get("cooking_time_minutes", 0) for meal in day.get("meals", []))
        daily_times.append(day_time)
        total_time += day_time
    
    return {
        "total_minutes": total_time,
        "average_per_day": round(total_time / len(daily_times), 1) if daily_times else 0,
        "max_day": max(daily_times) if daily_times else 0,
        "min_day": min(daily_times) if daily_times else 0,
        "daily_times": daily_times
    }


def find_ingredient_reuse(meal_plan_json: str) -> Dict:
    """Find ingredients used multiple times.
    
    Args:
        meal_plan_json: JSON string of meal plan
    
    Returns:
        Ingredient usage counts
    """
    try:
        plan = json.loads(meal_plan_json)
    except:
        return {"error": "Invalid meal plan JSON"}
    
    ingredient_counts = {}
    
    for day in plan:
        for meal in day.get("meals", []):
            for ing in meal.get("ingredients", []):
                name = ing.get("name", "").lower()
                ingredient_counts[name] = ingredient_counts.get(name, 0) + 1
    
    # Return items used 2+ times
    reused = {k: v for k, v in ingredient_counts.items() if v >= 2}
    
    return {
        "reused_ingredients": reused,
        "reuse_count": len(reused),
        "total_unique": len(ingredient_counts)
    }


# ============================================================================
# GROCERY LIST TOOLS
# ============================================================================

def aggregate_ingredients_for_shopping(meal_plan_json: str) -> Dict:
    """Aggregate all ingredients into shopping list.
    
    Args:
        meal_plan_json: JSON string of meal plan
    
    Returns:
        Aggregated shopping list
    """
    try:
        plan = json.loads(meal_plan_json)
    except:
        return {"error": "Invalid meal plan JSON"}
    
    aggregated = {}
    
    for day in plan:
        for meal in day.get("meals", []):
            for ing in meal.get("ingredients", []):
                name = ing.get("name", "").lower()
                amount = ing.get("amount", 0)
                
                if name in aggregated:
                    aggregated[name]["total_amount"] += amount
                    aggregated[name]["used_in_meals"].append(meal.get("name", ""))
                else:
                    aggregated[name] = {
                        "name": name.title(),
                        "total_amount": amount,
                        "unit": ing.get("unit", "grams"),
                        "used_in_meals": [meal.get("name", "")]
                    }
    
    # Calculate costs
    shopping_list = []
    total_cost = 0
    
    for name, data in aggregated.items():
        cost_info = estimate_ingredient_cost(name, data["total_amount"])
        item = {
            "name": data["name"],
            "amount": round(data["total_amount"], 1),
            "unit": data["unit"],
            "cost": cost_info["total_cost"],
            "used_in": len(data["used_in_meals"])
        }
        shopping_list.append(item)
        total_cost += cost_info["total_cost"]
    
    return {
        "shopping_list": sorted(shopping_list, key=lambda x: x["name"]),
        "total_items": len(shopping_list),
        "total_cost": round(total_cost, 2)
    }


# Export all tools
ALL_ADK_TOOLS = [
    # Profile Management
    create_household_profile,
    add_family_member,
    get_household_constraints,
    
    # Nutrition
    nutrition_lookup,
    calculate_recipe_nutrition,
    get_health_guidelines,
    check_allergens_in_recipe,
    
    # Cost
    estimate_ingredient_cost,
    calculate_meal_plan_cost,
    
    # Optimization
    analyze_cooking_time,
    find_ingredient_reuse,
    
    # Grocery
    aggregate_ingredients_for_shopping
]
