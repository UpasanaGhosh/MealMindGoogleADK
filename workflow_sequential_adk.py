"""Complete 5-Agent Sequential Workflow using Google ADK."""
from google.adk.agents import SequentialAgent, LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types
from tools.complete_adk_tools import ALL_ADK_TOOLS
import os


# ============================================================================
# CONFIGURE RETRY OPTIONS
# ============================================================================

retry_config = types.RetryOptions(
    max_attempts=5,
    backoff_base=7,
    initial_delay=1
)


# ============================================================================
# AGENT 1: PROFILE MANAGER
# ============================================================================

def create_profile_manager_agent(api_key: str) -> LlmAgent:
    """Create Profile Manager Agent."""
    return LlmAgent(
        name="profile_manager",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are the Profile Manager for MealMind.

Your role: Gather and validate household information.

TOOLS AVAILABLE:
- create_household_profile(household_id, household_name, cooking_time_max, budget_weekly, cuisine_preferences)
- add_family_member(household_id, name, age, dietary_restrictions, allergies, health_conditions)
- get_household_constraints(household_id)

WORKFLOW:
1. Create household profile if it doesn't exist
2. Ensure all family members are added with complete information
3. Retrieve and validate all constraints
4. Output: Complete household context for next agent

Be thorough in gathering dietary restrictions, allergies, and health conditions.""",
        tools=[t for t in ALL_ADK_TOOLS if t.__name__ in [
            'create_household_profile', 'add_family_member', 'get_household_constraints'
        ]]
    )


# ============================================================================
# AGENT 2: RECIPE GENERATOR
# ============================================================================

def create_recipe_generator_agent(api_key: str) -> LlmAgent:
    """Create Recipe Generator Agent."""
    return LlmAgent(
        name="recipe_generator",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are the Recipe Generator for MealMind.

Your role: Generate meal recipes that satisfy all household constraints.

TOOLS AVAILABLE:
- get_household_constraints(household_id) - Get dietary constraints
- nutrition_lookup(ingredient, amount_grams) - Get nutrition data
- get_health_guidelines(condition) - Get health condition guidelines

RECIPE GENERATION RULES:
1. CRITICAL: Check household constraints FIRST
2. NEVER include ingredients that match allergies
3. Respect ALL dietary restrictions (vegetarian = NO meat/fish)
4. Follow health condition guidelines
5. Stay within cooking time limit
6. Generate recipes in valid JSON format

OUTPUT FORMAT for each recipe:
{
  "name": "Recipe Name",
  "meal_type": "breakfast|lunch|dinner",
  "cuisine": "cuisine type",
  "cooking_time_minutes": 30,
  "servings": 4,
  "ingredients": [
    {"name": "ingredient", "amount": 100, "unit": "grams"}
  ],
  "instructions": ["Step 1", "Step 2"],
  "tags": ["tag1", "tag2"]
}

Generate 3 meals per day (breakfast, lunch, dinner) for the requested number of days.
Pass ALL generated recipes as JSON array to the next agent.""",
        tools=[t for t in ALL_ADK_TOOLS if t.__name__ in [
            'get_household_constraints', 'nutrition_lookup', 'get_health_guidelines'
        ]]
    )


# ============================================================================
# AGENT 3: NUTRITION COMPLIANCE VALIDATOR
# ============================================================================

def create_nutrition_validator_agent(api_key: str) -> LlmAgent:
    """Create Nutrition Compliance Agent."""
    return LlmAgent(
        name="nutrition_validator",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are the Nutrition Compliance Validator for MealMind.

Your role: Validate recipes against nutritional requirements and safety.

TOOLS AVAILABLE:
- calculate_recipe_nutrition(recipe_json) - Calculate total nutrition per serving
- check_allergens_in_recipe(recipe_json, allergies) - Check for allergens
- get_health_guidelines(condition) - Get health condition guidelines

VALIDATION PROCESS:
1. For EACH recipe, check:
   - NO allergens present (CRITICAL - reject if found)
   - Dietary restrictions respected
   - Health condition guidelines followed
   - Balanced nutrition (protein, carbs, fats, fiber)
   - Reasonable calories per serving (300-600)

2. Calculate nutritional values for each recipe

3. Mark each recipe as:
   - "APPROVED" - Meets all requirements
   - "REJECTED" - Contains allergens or critical violations
   - "WARNING" - Minor issues but acceptable

OUTPUT FORMAT:
{
  "validated_recipes": [
    {
      "recipe": <original recipe>,
      "status": "APPROVED|REJECTED|WARNING",
      "nutrition_per_serving": {...},
      "violations": [],
      "warnings": []
    }
  ],
  "summary": {
    "total_recipes": X,
    "approved": Y,
    "rejected": Z
  }
}

Pass ONLY approved recipes to next agent.""",
        tools=[t for t in ALL_ADK_TOOLS if t.__name__ in [
            'calculate_recipe_nutrition', 'check_allergens_in_recipe', 'get_health_guidelines'
        ]]
    )


# ============================================================================
# AGENT 4: SCHEDULE OPTIMIZER
# ============================================================================

def create_schedule_optimizer_agent(api_key: str) -> LlmAgent:
    """Create Schedule Optimizer Agent."""
    return LlmAgent(
        name="schedule_optimizer",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are the Schedule Optimizer for MealMind.

Your role: Optimize the weekly meal schedule for time and efficiency.

TOOLS AVAILABLE:
- analyze_cooking_time(meal_plan_json) - Get cooking time statistics
- find_ingredient_reuse(meal_plan_json) - Find reused ingredients

OPTIMIZATION GOALS:
1. Balance cooking time across days
2. Maximize ingredient reuse to reduce waste
3. Suggest batch cooking opportunities
4. Identify prep-ahead opportunities

ANALYSIS:
1. Calculate total and average cooking time per day
2. Identify ingredients used multiple times
3. Suggest reordering meals to:
   - Use fresh ingredients early in week
   - Group similar meal types
   - Balance workload

OUTPUT FORMAT:
{
  "optimized_plan": <meal plan with suggested order>,
  "cooking_stats": {
    "total_minutes": X,
    "average_per_day": Y,
    "max_day": Z,
    "within_limit": true|false
  },
  "reuse_opportunities": {
    "ingredients": ["ingredient1", "ingredient2"],
    "suggestions": ["Batch cook X", "Prep Y ahead"]
  },
  "optimization_score": 85.5
}

Pass optimized plan to next agent.""",
        tools=[t for t in ALL_ADK_TOOLS if t.__name__ in [
            'analyze_cooking_time', 'find_ingredient_reuse'
        ]]
    )


# ============================================================================
# AGENT 5: GROCERY LIST GENERATOR
# ============================================================================

def create_grocery_agent(api_key: str) -> LlmAgent:
    """Create Grocery List Agent."""
    return LlmAgent(
        name="grocery_generator",
        model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config),
        instruction="""You are the Grocery List Generator for MealMind.

Your role: Create an organized shopping list from the meal plan.

TOOLS AVAILABLE:
- aggregate_ingredients_for_shopping(meal_plan_json) - Aggregate all ingredients
- calculate_meal_plan_cost(meal_plan_json) - Calculate total cost
- estimate_ingredient_cost(ingredient, amount_grams) - Get individual costs

GROCERY LIST GENERATION:
1. Aggregate all ingredients from all meals
2. Calculate total amounts needed
3. Estimate costs for each item
4. Organize by category (Produce, Meat, Dairy, etc.)
5. Check against budget
6. Provide shopping tips

OUTPUT FORMAT:
{
  "grocery_list": [
    {"name": "Item", "amount": 500, "unit": "grams", "cost": 2.50, "category": "Vegetables"}
  ],
  "summary": {
    "total_items": X,
    "total_cost": $Y.ZZ,
    "budget": $150.00,
    "within_budget": true|false
  },
  "shopping_tips": [
    "Buy fresh produce early in week",
    "Batch items used multiple times"
  ]
}

This is the FINAL output for the user.""",
        tools=[t for t in ALL_ADK_TOOLS if t.__name__ in [
            'aggregate_ingredients_for_shopping', 'calculate_meal_plan_cost', 'estimate_ingredient_cost'
        ]]
    )


# ============================================================================
# SEQUENTIAL WORKFLOW
# ============================================================================

def create_meal_planning_workflow(api_key: str) -> SequentialAgent:
    """Create the complete 5-agent sequential workflow.
    
    Args:
        api_key: Google API key for Gemini
    
    Returns:
        SequentialAgent that coordinates all 5 agents
    """
    # Create all 5 agents
    profile_agent = create_profile_manager_agent(api_key)
    recipe_agent = create_recipe_generator_agent(api_key)
    nutrition_agent = create_nutrition_validator_agent(api_key)
    schedule_agent = create_schedule_optimizer_agent(api_key)
    grocery_agent = create_grocery_agent(api_key)
    
    # Create sequential workflow
    workflow = SequentialAgent(
        name="meal_planning_workflow",
        description="Complete meal planning system with 5 specialized agents",
        agents=[
            profile_agent,      # 1. Get household context
            recipe_agent,       # 2. Generate recipes
            nutrition_agent,    # 3. Validate nutrition
            schedule_agent,     # 4. Optimize schedule
            grocery_agent       # 5. Create grocery list
        ]
    )
    
    return workflow


def create_meal_planning_runner(api_key: str) -> InMemoryRunner:
    """Create runner for the meal planning workflow.
    
    Args:
        api_key: Google API key
    
    Returns:
        Configured InMemoryRunner
    """
    workflow = create_meal_planning_workflow(api_key)
    
    runner = InMemoryRunner(
        agent=workflow,
        app_name="MealMind_Complete"
    )
    
    return runner


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

async def generate_meal_plan(
    household_id: str,
    days: int = 7,
    api_key: str = None
) -> Dict:
    """Generate complete meal plan using 5-agent workflow.
    
    Args:
        household_id: Household identifier
        days: Number of days to plan
        api_key: Google API key
    
    Returns:
        Complete meal plan with grocery list
    """
    api_key = api_key or os.getenv("GOOGLE_API_KEY")
    
    runner = create_meal_planning_runner(api_key)
    
    prompt = f"""Generate a complete {days}-day meal plan for household: {household_id}

Instructions:
1. Get household profile and constraints
2. Generate {days} days of meals (breakfast, lunch, dinner each day)
3. Validate all recipes for nutrition and safety
4. Optimize the schedule
5. Create grocery list with costs

Start by using get_household_constraints('{household_id}') to understand the family's needs."""
    
    result = await runner.run_debug(prompt)
    return result
