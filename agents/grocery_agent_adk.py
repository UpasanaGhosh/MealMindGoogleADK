"""Grocery List Agent - ADK implementation."""
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

def create_grocery_agent(retry_config: types.RetryOptions) -> LlmAgent:
    """Create Grocery List Agent."""
    from tools import aggregate_ingredients_for_shopping, estimate_ingredient_cost
    
    return LlmAgent(
        name="grocery_generator",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are the Grocery List Generator.

Create organized shopping lists from meal plans.
Aggregate ingredients. Calculate costs. Check budget.
Provide shopping tips. This is FINAL output.""",
        tools=[aggregate_ingredients_for_shopping, estimate_ingredient_cost]
    )
