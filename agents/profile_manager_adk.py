"""Profile Manager Agent - ADK implementation."""
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

def create_profile_manager_agent(retry_config: types.RetryOptions) -> LlmAgent:
    """Create Profile Manager Agent."""
    from tools import create_household_profile, add_family_member, get_household_constraints
    
    return LlmAgent(
        name="profile_manager",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are the Profile Manager for MealMind.
        
Your role: Gather and validate household information.

Use create_household_profile, add_family_member, get_household_constraints.
Output complete household context for next agent.""",
        tools=[create_household_profile, add_family_member, get_household_constraints]
    )
