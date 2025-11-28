"""Simplified 3-Agent Orchestrator using Google ADK Sequential Workflow."""
from google.adk.agents import SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types
from agents import (
    create_recipe_generator_agent,
    create_nutrition_validator_agent,
    create_meal_coordinator_agent
)
from utils import optimize_schedule, generate_grocery_list
import os


# Configure retry options
retry_config = types.RetryOptions(
    max_attempts=5,
    backoff_base=7,
    initial_delay=1
)


class MealPlanOrchestrator:
    """Orchestrates 3 LLM agents + Python utilities for meal planning."""
    
    def __init__(self, api_key: str = None):
        """Initialize orchestrator.
        
        Args:
            api_key: Google API key for Gemini
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        # Create 3 LLM agents
        self.recipe_agent = create_recipe_generator_agent(self.api_key, retry_config)
        self.nutrition_agent = create_nutrition_validator_agent(self.api_key, retry_config)
        self.coordinator_agent = create_meal_coordinator_agent(self.api_key, retry_config)
        
        # Create sequential workflow (3 agents only)
        self.workflow = SequentialAgent(
            name="meal_planning_workflow",
            description="3-agent meal planning system with Python utilities",
            agents=[
                self.recipe_agent,       # 1. Generate recipes
                self.nutrition_agent,    # 2. Validate safety
                self.coordinator_agent   # 3. Coordinate final output
            ]
        )
        
        # Create runner
        self.runner = InMemoryRunner(agent=self.workflow)
    
    async def generate_meal_plan(
        self,
        household_id: str,
        days: int = 3
    ) -> dict:
        """Generate complete meal plan.
        
        Args:
            household_id: Household identifier  
            days: Number of days to plan
        
        Returns:
            Complete meal plan with grocery list
        """
        prompt = f"""Generate a complete {days}-day meal plan for household: {household_id}

WORKFLOW:
1. Recipe Generator: Create {days*3} recipes (breakfast, lunch, dinner per day)
2. Nutrition Validator: Validate each recipe for safety
3. Meal Coordinator: Format final output

Start by checking household constraints with get_household_constraints('{household_id}')."""
        
        result = await self.runner.run_debug(prompt)
        
        # Post-process with Python utilities (outside LLM)
        try:
            if isinstance(result, str):
                import json
                meal_data = json.loads(result)
            else:
                meal_data = result
            
            if "days" in meal_data or "meal_plan" in meal_data:
                meals = meal_data.get("days") or meal_data.get("meal_plan", [])
                
                # Run Python utilities
                optimization = optimize_schedule(meals, 45)
                grocery = generate_grocery_list(meals, 150.0)
                
                # Add to result
                final_result = {
                    "meal_plan": meals,
                    "optimization": optimization,
                    "grocery_list": grocery,
                    "status": "complete"
                }
                return final_result
        except:
            pass
        
        return result


# Factory function
def create_orchestrator(api_key: str = None) -> MealPlanOrchestrator:
    """Create orchestrator instance.
    
    Args:
        api_key: Google API key
    
    Returns:
        Configured orchestrator with 3 agents
    """
    return MealPlanOrchestrator(api_key=api_key)
