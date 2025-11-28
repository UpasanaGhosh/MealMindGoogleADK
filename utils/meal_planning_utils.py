"""Pure Python utilities for meal planning (no LLM needed)."""
import json
from typing import Dict, List
from collections import defaultdict


def optimize_schedule(meal_plan: List[Dict], cooking_time_max: int = 45) -> Dict:
    """Optimize meal schedule using Python algorithms (no LLM).
    
    Args:
        meal_plan: List of daily meal plans
        cooking_time_max: Maximum cooking time per day
    
    Returns:
        Optimization results with stats and suggestions
    """
    # Calculate cooking time stats
    daily_times = []
    for day in meal_plan:
        day_time = sum(meal.get("cooking_time_minutes", 0) for meal in day.get("meals", []))
        daily_times.append(day_time)
    
    total_time = sum(daily_times)
    avg_time = round(total_time / len(daily_times), 1) if daily_times else 0
    
    # Find ingredient reuse
    ingredient_counts = defaultdict(int)
    for day in meal_plan:
        for meal in day.get("meals", []):
            for ing in meal.get("ingredients", []):
                ingredient_counts[ing.get("name", "").lower()] += 1
    
    reused_ingredients = {k: v for k, v in ingredient_counts.items() if v >= 2}
    
    # Generate suggestions
    suggestions = []
    if avg_time > cooking_time_max:
        suggestions.append(f"Average time ({avg_time} min) exceeds target. Consider simpler recipes.")
    
    if reused_ingredients:
        batch_items = list(reused_ingredients.keys())[:3]
        suggestions.append(f"Batch cook: {', '.join(batch_items)}")
    
    # Calculate score
    score = 100.0
    if avg_time > cooking_time_max:
        score -= ((avg_time - cooking_time_max) / cooking_time_max) * 30
    
    reuse_ratio = len(reused_ingredients) / len(ingredient_counts) if ingredient_counts else 0
    score += reuse_ratio * 15
    
    return {
        "cooking_stats": {
            "total_minutes": total_time,
            "average_per_day": avg_time,
            "max_day": max(daily_times) if daily_times else 0,
            "within_limit": avg_time <= cooking_time_max
        },
        "reused_ingredients": reused_ingredients,
        "optimization_score": round(max(0, min(100, score)), 1),
        "suggestions": suggestions
    }


def generate_grocery_list(meal_plan: List[Dict], budget: float = 150.0, cost_db: Dict = None) -> Dict:
    """Generate grocery list using Python aggregation (no LLM).
    
    Args:
        meal_plan: List of daily meal plans
        budget: Weekly budget
        cost_db: Cost database for estimation
    
    Returns:
        Complete grocery list with costs
    """
    if cost_db is None:
        cost_db = {
            "chicken breast": 1.20, "brown rice": 0.15, "broccoli": 0.40,
            "salmon": 2.50, "quinoa": 0.80, "tofu": 0.90
        }
    
    # Aggregate ingredients
    aggregated = defaultdict(lambda: {"total_amount": 0, "unit": "grams", "meals": []})
    
    for day in meal_plan:
        for meal in day.get("meals", []):
            meal_name = meal.get("name", "")
            for ing in meal.get("ingredients", []):
                name = ing.get("name", "").lower()
                aggregated[name]["total_amount"] += ing.get("amount", 0)
                aggregated[name]["unit"] = ing.get("unit", "grams")
                aggregated[name]["meals"].append(meal_name)
    
    # Calculate costs
    shopping_list = []
    total_cost = 0
    
    for name, data in aggregated.items():
        cost_per_100g = cost_db.get(name, 0.50)
        item_cost = (data["total_amount"] / 100.0) * cost_per_100g
        
        shopping_list.append({
            "name": name.title(),
            "amount": round(data["total_amount"], 1),
            "unit": data["unit"],
            "cost": round(item_cost, 2),
            "used_in": len(data["meals"])
        })
        total_cost += item_cost
    
    # Sort by name
    shopping_list.sort(key=lambda x: x["name"])
    
    # Generate tips
    tips = []
    if total_cost <= budget:
        tips.append(f"✓ Within budget! ${round(budget - total_cost, 2)} remaining")
    else:
        tips.append(f"⚠️ Over budget by ${round(total_cost - budget, 2)}")
    
    frequent_items = [item["name"] for item in shopping_list if item["used_in"] >= 3]
    if frequent_items:
        tips.append(f"Buy in bulk: {', '.join(frequent_items[:3])}")
    
    return {
        "shopping_list": shopping_list,
        "total_items": len(shopping_list),
        "total_cost": round(total_cost, 2),
        "budget": budget,
        "within_budget": total_cost <= budget,
        "shopping_tips": tips
    }


def calculate_optimization_score(cooking_stats: Dict, reuse_count: int, total_ingredients: int) -> float:
    """Calculate optimization score (pure Python)."""
    score = 100.0
    
    if cooking_stats.get("average_per_day", 0) > 45:
        score -= 20
    
    if total_ingredients > 0:
        reuse_ratio = reuse_count / total_ingredients
        score += reuse_ratio * 15
    
    return round(max(0, min(100, score)), 1)
