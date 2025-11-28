"""Cost estimation tools."""
from typing import Dict
import json

COST_DB = {
    "chicken breast": 1.20, "brown rice": 0.15, "broccoli": 0.40,
    "salmon": 2.50, "quinoa": 0.80, "spinach": 0.60,
    "sweet potato": 0.30, "eggs": 0.25, "olive oil": 1.00, "tofu": 0.90
}


def estimate_ingredient_cost(ingredient: str, amount_grams: float) -> Dict:
    """Estimate cost for an ingredient."""
    ingredient_lower = ingredient.lower()
    
    if ingredient_lower in COST_DB:
        cost_per_100g = COST_DB[ingredient_lower]
        total_cost = (amount_grams / 100.0) * cost_per_100g
        return {"ingredient": ingredient, "amount_grams": amount_grams, "total_cost": round(total_cost, 2)}
    
    estimated = (amount_grams / 100.0) * 0.50
    return {"ingredient": ingredient, "amount_grams": amount_grams, "total_cost": round(estimated, 2), "note": "Estimated"}


def calculate_meal_plan_cost(meal_plan_json: str) -> Dict:
    """Calculate total cost for a meal plan."""
    try:
        plan = json.loads(meal_plan_json)
        total_cost = 0.0
        daily_costs = []
        
        for day in plan:
            day_cost = 0.0
            for meal in day.get("meals", []):
                for ing in meal.get("ingredients", []):
                    cost_info = estimate_ingredient_cost(ing.get("name", ""), ing.get("amount", 0))
                    day_cost += cost_info["total_cost"]
            daily_costs.append(round(day_cost, 2))
            total_cost += day_cost
        
        return {"total_cost": round(total_cost, 2), "daily_costs": daily_costs, "average_per_day": round(total_cost / len(daily_costs), 2) if daily_costs else 0}
    except:
        return {"error": "Invalid JSON"}
