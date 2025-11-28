"""ADK Recipe Generator Agent using google.adk framework."""
from typing import Any, Dict, List
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from tools.adk_tools import adk_tools


class RecipeGeneratorADK:
    """Recipe Generator using Google ADK LlmAgent."""
    
    def __init__(self, api_key: str = None):
        """Initialize ADK Recipe Generator.
        
        Args:
            api_key: Google API key for Gemini
        """
        # Create Gemini model
        self.model = Gemini(
            model="gemini-2.0-flash-exp",
            api_key=api_key
        )
        
        # Create LlmAgent with tools
        self.agent = LlmAgent(
            model=self.model,
            name="recipe_generator",
            description="Generates healthy meal recipes with nutritional analysis",
            tools=adk_tools,
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the recipe agent."""
        return """You are MealMind's Recipe Generator, specialized in creating healthy, nutritious meal recipes.

CAPABILITIES:
- Generate complete recipes with ingredients and instructions
- Look up nutritional information for ingredients
- Consider household dietary constraints and preferences
- Estimate ingredient costs for budget planning

TOOLS AVAILABLE:
1. nutrition_lookup_adk(ingredient, amount_grams) - Get nutritional data
2. get_household_constraints_adk(household_id) - Get dietary restrictions
3. estimate_cost_adk(ingredient, amount_grams) - Get cost estimates

RECIPE FORMAT:
Generate recipes in this structure:
{
  "name": "Recipe Name",
  "servings": 4,
  "prep_time": "15 minutes",
  "cook_time": "30 minutes",
  "ingredients": [
    {"name": "ingredient", "amount": "1 cup", "grams": 150}
  ],
  "instructions": ["Step 1...", "Step 2..."],
  "nutrition_per_serving": {
    "calories": 400,
    "protein_g": 25,
    "carbs_g": 45,
    "fat_g": 12,
    "fiber_g": 8
  },
  "estimated_cost": "$12.50 total ($3.13 per serving)"
}

GUIDELINES:
- Always use tools to verify nutrition and costs
- Respect dietary constraints from household profile
- Focus on balanced, healthy meals
- Provide clear, step-by-step instructions
- Include nutritional breakdown per serving
"""
    
    def generate_recipe(self, 
                       prompt: str, 
                       household_id: str = "default",
                       session_id: str = "recipe_session") -> Dict[str, Any]:
        """Generate a recipe using ADK agent.
        
        Args:
            prompt: Recipe generation prompt
            household_id: Household ID for constraints
            session_id: Session identifier
            
        Returns:
            Generated recipe dictionary
        """
        # Enhance prompt with household context
        enhanced_prompt = f"""
Generate a recipe for: {prompt}

Household ID: {household_id}

Please:
1. First check household constraints using get_household_constraints_adk
2. Generate a recipe that respects those constraints
3. Use nutrition_lookup_adk to verify nutritional content
4. Use estimate_cost_adk to calculate total cost
5. Return a complete recipe in the specified JSON format
"""
        
        # Generate response using ADK agent
        response = self.agent.run(enhanced_prompt, session_id=session_id)
        return response
    
    def get_agent(self) -> LlmAgent:
        """Get the underlying ADK agent."""
        return self.agent
