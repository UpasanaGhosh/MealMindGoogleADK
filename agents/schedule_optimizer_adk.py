"""Schedule Optimizer Agent - ADK implementation."""
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types

def create_schedule_optimizer_agent(retry_config: types.RetryOptions) -> LlmAgent:
    """Create Schedule Optimizer Agent."""
    from tools import analyze_cooking_time, find_ingredient_reuse
    
    return LlmAgent(
        name="schedule_optimizer",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are the Schedule Optimizer.

Optimize meal schedules for time and efficiency.
Analyze cooking time. Find ingredient reuse.
Suggest batch cooking. Balance workload.""",
        tools=[analyze_cooking_time, find_ingredient_reuse]
    )
