"""Nutrition Compliance Agent - ADK implementation."""
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

def create_nutrition_validator_agent(retry_config: types.RetryOptions) -> LlmAgent:
    """Create Nutrition Compliance Agent."""
    from tools import calculate_recipe_nutrition, check_allergens_in_recipe, get_health_guidelines
    
    return LlmAgent(
        name="nutrition_validator",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are the Nutrition Compliance Validator.

Validate recipes for safety and nutrition.
Check allergens (CRITICAL). Calculate nutrition.
Approve/reject each recipe. Pass only APPROVED recipes forward.""",
        tools=[calculate_recipe_nutrition, check_allergens_in_recipe, get_health_guidelines]
    )
