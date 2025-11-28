"""Demo script for complete 5-agent MealMind system with Google ADK."""
import os
import json
import asyncio
from dotenv import load_dotenv
from workflow_sequential_adk import create_meal_planning_runner
from tools.complete_adk_tools import (
    create_household_profile,
    add_family_member,
    get_household_constraints
)

load_dotenv()


async def main():
    """Run complete 5-agent demo."""
    print("🚀 MealMind Complete 5-Agent System Demo")
    print("=" * 70)
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found")
        print("Please set it in .env file")
        return
    
    # Step 1: Create household profile
    print("\n📋 Step 1: Creating household profile...")
    household = create_household_profile(
        household_id="demo_family",
        household_name="Demo Family",
        cooking_time_max=45,
        budget_weekly=150.0,
        cuisine_preferences="Mediterranean, Indian, Mexican"
    )
    print(f"✅ Household created: {household['household_name']}")
    
    # Step 2: Add family members
    print("\n👨‍👩‍👦 Step 2: Adding family members...")
    
    add_family_member(
        household_id="demo_family",
        name="Alice",
        age=35,
        dietary_restrictions="vegetarian",
        allergies="",
        health_conditions="PCOS"
    )
    print("  ✅ Added Alice (vegetarian, PCOS)")
    
    add_family_member(
        household_id="demo_family",
        name="Bob",
        age=33,
        dietary_restrictions="",
        allergies="nuts",
        health_conditions="diabetes"
    )
    print("  ✅ Added Bob (nut allergy, diabetes)")
    
    add_family_member(
        household_id="demo_family",
        name="Charlie",
        age=8,
        dietary_restrictions="",
        allergies="",
        health_conditions=""
    )
    print("  ✅ Added Charlie (no restrictions)")
    
    # Step 3: View constraints
    print("\n🔍 Step 3: Household constraints:")
    constraints = get_household_constraints("demo_family")
    print(json.dumps(constraints, indent=2))
    
    # Step 4: Create runner
    print("\n🤖 Step 4: Initializing 5-agent workflow...")
    runner = create_meal_planning_runner(api_key)
    print("✅ Workflow ready:")
    print("   1. Profile Manager")
    print("   2. Recipe Generator")
    print("   3. Nutrition Validator")
    print("   4. Schedule Optimizer")
    print("   5. Grocery Generator")
    
    # Step 5: Generate meal plan
    print("\n🍽️  Step 5: Generating 3-day meal plan...")
    print("This will take 2-3 minutes as all 5 agents process...")
    print("-" * 70)
    
    prompt = """Generate a complete 3-day meal plan for household demo_family.

WORKFLOW:
1. Profile Manager: Get household constraints
2. Recipe Generator: Generate 9 recipes (3 days × 3 meals)
   - Alice is vegetarian with PCOS
   - Bob has nut allergy and diabetes
   - Charlie has no restrictions
   - Max 45 min cooking per day
   - Budget: $150/week
3. Nutrition Validator: Validate each recipe
4. Schedule Optimizer: Optimize the schedule
5. Grocery Generator: Create shopping list

Start by getting household constraints."""
    
    try:
        result = await runner.run_debug(prompt)
        
        print("\n✅ MEAL PLAN GENERATED SUCCESSFULLY!")
        print("=" * 70)
        print(result)
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
    
    print("\n🎉 Demo complete!")


if __name__ == "__main__":
    asyncio.run(main())
