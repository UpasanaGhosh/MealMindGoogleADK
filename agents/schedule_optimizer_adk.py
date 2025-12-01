"""Meal Coordinator Agent - Orchestrates final steps using Python utilities."""
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types


def create_meal_coordinator_agent(api_key: str, retry_config: types.RetryOptions) -> LlmAgent:
    """Create Meal Coordinator Agent.
    
    This agent coordinates the final steps by calling Python utilities
    for schedule optimization and grocery list generation.
    """
    return LlmAgent(
        name="meal_coordinator",
        model=Gemini(model="gemini-2.5-flash-lite", api_key=api_key, retry_options=retry_config),
        instruction="""You are the Meal Coordinator for MealMind.

Your role: Finalize the meal plan using Python utilities.

WORKFLOW:
1. Receive validated recipes from previous agent
2. Call Python utilities (NOT tools, just explain you'll use them):
   - optimize_schedule() for cooking time analysis
   - generate_grocery_list() for shopping list
3. Format the final comprehensive output

OUTPUT FORMAT:
{
  "meal_plan": {
    "days": [...validated recipes...],
    "optimization": {
      "cooking_stats": {...},
      "score": X.X,
      "suggestions": [...]
    },
    "grocery_list": {
      "items": [...],
      "total_cost": $X.XX,
      "tips": [...]
    }
  }
}

Provide a complete, user-friendly meal planning summary.""",
        tools=[]  # No tools - uses Python utilities
    )
