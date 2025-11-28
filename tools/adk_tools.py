"""ADK-compliant tools using google.adk structure."""
from typing import Dict
from google.adk.tools.tool_context import ToolContext
from tools.nutrition_lookup import nutrition_tool
from tools.family_profile_store import profile_store
from tools.ingredient_cost_estimator import cost_estimator


def nutrition_lookup_adk(context: ToolContext, ingredient: str, amount_grams: float = 100.0) -> Dict:
    """Look up nutritional information for an ingredient (ADK tool).
    
    Args:
        context: ADK ToolContext
        ingredient: Name of ingredient
        amount_grams: Amount in grams
    
    Returns:
        Nutritional information dictionary
    """
    result = nutrition_tool.lookup(ingredient, amount_grams)
    return result.model_dump()


def get_household_constraints_adk(context: ToolContext, household_id: str) -> Dict:
    """Get household dietary constraints (ADK tool).
    
    Args:
        context: ADK ToolContext
        household_id: Household identifier
    
    Returns:
        Constraints dictionary
    """
    return profile_store.get_all_constraints(household_id)


def estimate_cost_adk(context: ToolContext, ingredient: str, amount_grams: float) -> Dict:
    """Estimate ingredient cost (ADK tool).
    
    Args:
        context: ADK ToolContext
        ingredient: Ingredient name
        amount_grams: Amount in grams
    
    Returns:
        Cost information dictionary
    """
    result = cost_estimator.estimate_ingredient_cost(ingredient, amount_grams)
    return result.model_dump()


# Export ADK tools
adk_tools = [
    nutrition_lookup_adk,
    get_household_constraints_adk,
    estimate_cost_adk
]
