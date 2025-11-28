"""Recipe Generator Agent - ADK implementation."""
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

def create_recipe_generator_agent(retry_config: types.RetryOptions) -> LlmAgent:
    """Create Recipe Generator Agent."""
    from tools import get_household_constraints, nutrition_lookup, get_health_guidelines
    
    return LlmAgent(
        name="recipe_generator",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are the Recipe Generator for MealMind.

Generate meal recipes that satisfy all household constraints.
Check constraints FIRST. NO allergens. Respect dietary restrictions.
Output recipes as JSON array.""",
        tools=[get_household_constraints, nutrition_lookup, get_health_guidelines]
    )
