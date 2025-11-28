"""Nutrition lookup tools."""
from typing import Dict
import json

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
    
    return {
        "ingredient": ingredient,
        "amount_grams": amount_grams,
        "calories": 100.0,
        "protein_g": 5.0,
        "carbs_g": 15.0,
        "fat_g": 3.0,
        "fiber_g": 2.0,
        "note": "Estimated values"
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
        
        for key in total:
            total[key] += nutrition.get(key, 0)
    
    servings = recipe.get("servings", 4)
    per_serving = {k: round(v / servings, 2) for k, v in total.items()}
    per_serving["servings"] = servings
    
    return per_serving
