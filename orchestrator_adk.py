"""ADK Orchestrator using Runner and InMemorySessionService."""
from typing import Any, Dict, List
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.apps.app import App, EventsCompactionConfig
from agents.recipe_generator_adk import RecipeGeneratorADK
import os
import structlog

logger = structlog.get_logger(__name__)


class MealPlanOrchestratorADK:
    """ADK-based orchestrator for meal planning."""
    
    def __init__(self, api_key: str = None):
        """Initialize ADK orchestrator.
        
        Args:
            api_key: Google API key for Gemini
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        # Initialize ADK components
        self.session_service = InMemorySessionService()
        self.recipe_agent = RecipeGeneratorADK(api_key=self.api_key)
        
        # Create Runner
        self.runner = Runner(
            agent=self.recipe_agent.get_agent(),
            session_service=self.session_service
        )
        
        # Create App with configuration
        self.app = App(
            agent=self.recipe_agent.get_agent(),
            app_name="MealMind",
            events_compaction_config=EventsCompactionConfig(
                enabled=True,
                max_events=1000
            )
        )
        
        logger.info("ADK orchestrator initialized successfully")
    
    def generate_meal_plan(self, 
                          household_id: str,
                          preferences: Dict[str, Any],
                          num_days: int = 7) -> Dict[str, Any]:
        """Generate complete meal plan using ADK.
        
        Args:
            household_id: Household identifier
            preferences: Meal preferences and constraints
            num_days: Number of days to plan
            
        Returns:
            Complete meal plan with recipes
        """
        session_id = f"mealplan_{household_id}_{num_days}days"
        
        logger.info("Generating meal plan", 
                   household_id=household_id, 
                   num_days=num_days)
        
        # Create comprehensive prompt
        prompt = self._create_meal_plan_prompt(preferences, num_days)
        
        # Use Runner to execute
        try:
            result = self.runner.run(
                message=prompt,
                session_id=session_id
            )
            
            logger.info("Meal plan generated successfully",
                       session_id=session_id)
            
            return {
                "status": "success",
                "meal_plan": result,
                "session_id": session_id,
                "household_id": household_id
            }
            
        except Exception as e:
            logger.error("Failed to generate meal plan", 
                        error=str(e),
                        session_id=session_id)
            return {
                "status": "error",
                "error": str(e),
                "session_id": session_id
            }
    
    def _create_meal_plan_prompt(self, preferences: Dict, num_days: int) -> str:
        """Create comprehensive meal planning prompt."""
        return f"""
Generate a complete {num_days}-day meal plan with the following requirements:

PREFERENCES: {preferences}

REQUIREMENTS:
1. Check household constraints for dietary restrictions
2. Create {num_days} days of meals (breakfast, lunch, dinner)
3. Each meal should include:
   - Complete recipe with ingredients and instructions
   - Nutritional analysis using nutrition_lookup_adk
   - Cost estimates using estimate_cost_adk
4. Ensure nutritional balance across all days
5. Vary ingredients to avoid repetition
6. Consider prep time and cooking complexity

OUTPUT FORMAT:
Return a structured meal plan with:
- Daily meals organized by day
- Shopping list with total costs
- Nutritional summary for the week
- Prep time estimates

Please use all available tools to ensure accuracy.
"""
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get session conversation history.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of session events
        """
        return self.session_service.get_session_events(session_id)
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session.
        
        Args:
            session_id: Session to clear
            
        Returns:
            Success status
        """
        try:
            self.session_service.clear_session(session_id)
            logger.info("Session cleared", session_id=session_id)
            return True
        except Exception as e:
            logger.error("Failed to clear session", 
                        session_id=session_id, 
                        error=str(e))
            return False
    
    def get_app(self) -> App:
        """Get the ADK App instance."""
        return self.app
    
    def get_runner(self) -> Runner:
        """Get the ADK Runner instance."""
        return self.runner


# Factory function for easy instantiation
def create_adk_orchestrator(api_key: str = None) -> MealPlanOrchestratorADK:
    """Create ADK orchestrator instance.
    
    Args:
        api_key: Google API key
        
    Returns:
        Configured ADK orchestrator
    """
    return MealPlanOrchestratorADK(api_key=api_key)
