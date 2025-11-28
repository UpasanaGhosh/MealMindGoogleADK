"""Health guidelines and allergen checking tools."""
from typing import Dict
import json

HEALTH_GUIDELINES = {
    "diabetes": {"avoid": ["sugar", "white bread", "white rice"], "prefer": ["whole grains", "vegetables", "lean protein"]},
    "pcos": {"avoid": ["refined carbs", "sugar"], "prefer": ["low-GI foods", "vegetables", "lean protein"]},
    "high blood pressure": {"avoid": ["high sodium", "processed meats"], "prefer": ["fruits", "vegetables", "whole grains"]}
}

def get_health_guidelines(condition: str) -> Dict:
    """Get dietary guidelines for a health condition."""
    return HEALTH_GUIDELINES.get(condition.lower(), {"avoid": [], "prefer": [], "note": f"No guidelines for {condition}"})

def check_allergens_in_recipe(recipe_json: str, allergies: str) -> Dict:
    """Check if recipe contains allergens."""
    try:
        recipe = json.loads(recipe_json)
        allergy_list = [a.strip().lower() for a in allergies.split(",") if a.strip()]
        found = []
        for ing in recipe.get("ingredients", []):
            ing_name = ing.get("name", "").lower()
            for allergen in allergy_list:
                if allergen in ing_name: found.append(f"{allergen} in {ing.get('name')}")
        return {"has_allergens": len(found) > 0, "found_allergens": found}
    except: return {"error": "Invalid JSON"}
