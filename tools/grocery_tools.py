"""Grocery list tools."""
from typing import Dict
import json
from .cost_estimator import estimate_ingredient_cost

def aggregate_ingredients_for_shopping(meal_plan_json: str) -> Dict:
    """Aggregate all ingredients into shopping list."""
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
                        aggregated[name] = {"name": name.title(), "total_amount": ing.get("amount", 0), "unit": ing.get("unit", "grams")}
        shopping_list = []
        total_cost = 0
        for name, data in aggregated.items():
            cost_info = estimate_ingredient_cost(name, data["total_amount"])
            shopping_list.append({"name": data["name"], "amount": round(data["total_amount"], 1), "unit": data["unit"], "cost": cost_info["total_cost"]})
            total_cost += cost_info["total_cost"]
        return {"shopping_list": sorted(shopping_list, key=lambda x: x["name"]), "total_items": len(shopping_list), "total_cost": round(total_cost, 2)}
    except: return {"error": "Invalid JSON"}
