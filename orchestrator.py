"""Multi-Agent Orchestrator using Google ADK Sequential Workflow."""
from google.adk.agents import SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types
from agents import (
    create_profile_manager_agent,
    create_recipe_generator_agent,
    create_nutrition_validator_agent,
    create_schedule_optimizer_agent,
    create_grocery_agent
)
import os


# Configure retry options
retry_config = types.RetryOptions(
    max_attempts=5,
    backoff_base=7,
    initial_delay=1
)


class MealPlanOrchestrator:
    """Orchestrates 5 specialized agents using Sequential workflow."""
    
    def __init__(self, api_key: str = None):
        """Initialize orchestrator with all agents.
        
        Args:
            api_key: Google API key for Gemini
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        # Create all 5 agents
        self.profile_agent = create_profile_manager_agent(retry_config)
        self.recipe_agent = create_recipe_generator_agent(retry_config)
        self.nutrition_agent = create_nutrition_validator_agent(retry_config)
        self.schedule_agent = create_schedule_optimizer_agent(retry_config)
        self.grocery_agent = create_grocery_agent(retry_config)
        
        # Create sequential workflow
        self.workflow = SequentialAgent(
            name="meal_planning_workflow",
            description="Complete 5-agent meal planning system",
            agents=[
                self.profile_agent,
                self.recipe_agent,
                self.nutrition_agent,
                self.schedule_agent,
                self.grocery_agent
            ]
        )
        
        # Create runner
        self.runner = InMemoryRunner(agent=self.workflow)
    
    async def generate_meal_plan(
        self,
        household_id: str,
        days: int = 7
    ) -> dict:
        """Generate complete meal plan.
        
        Args:
            household_id: Household identifier
            days: Number of days to plan
        
        Returns:
            Complete meal plan with grocery list
        """
        prompt = f"""Generate a complete {days}-day meal plan for household: {household_id}

Instructions:
1. Get household profile and constraints
2. Generate {days} days of meals (breakfast, lunch, dinner)
3. Validate all recipes for nutrition and safety
4. Optimize the schedule
5. Create grocery list with costs

Start by using get_household_constraints('{household_id}')."""
        
        result = await self.runner.run_debug(prompt)
        return result


# Factory function
def create_orchestrator(api_key: str = None) -> MealPlanOrchestrator:
    """Create orchestrator instance.
    
    Args:
        api_key: Google API key
    
    Returns:
        Configured orchestrator
    """
    return MealPlanOrchestrator(api_key=api_key)
