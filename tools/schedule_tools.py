"""Schedule optimization tools."""
from typing import Dict
import json

def analyze_cooking_time(meal_plan_json: str) -> Dict:
    """Analyze cooking times across meal plan."""
    try:
        plan = json.loads(meal_plan_json)
        daily_times = [sum(m.get("cooking_time_minutes", 0) for m in day.get("meals", [])) for day in plan]
        total = sum(daily_times)
        return {"total_minutes": total, "average_per_day": round(total / len(daily_times), 1) if daily_times else 0, "max_day": max(daily_times) if daily_times else 0, "min_day": min(daily_times) if daily_times else 0, "daily_times": daily_times}
    except: return {"error": "Invalid JSON"}

def find_ingredient_reuse(meal_plan_json: str) -> Dict:
    """Find ingredients used multiple times."""
    try:
        plan = json.loads(meal_plan_json)
        counts = {}
        for day in plan:
            for meal in day.get("meals", []):
                for ing in meal.get("ingredients", []):
                    name = ing.get("name", "").lower()
                    counts[name] = counts.get(name, 0) + 1
        reused = {k: v for k, v in counts.items() if v >= 2}
        return {"reused_ingredients": reused, "reuse_count": len(reused), "total_unique": len(counts)}
    except: return {"error": "Invalid JSON"}
