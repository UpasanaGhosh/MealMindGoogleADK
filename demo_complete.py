"""Complete demo for 5-agent MealMind system."""
import os
import json
import asyncio
from dotenv import load_dotenv
from orchestrator import create_orchestrator
from tools import create_household_profile, add_family_member, get_household_constraints

load_dotenv()


async def main():
    """Run complete 5-agent demo."""
    print("🚀 MealMind Complete 5-Agent System")
    print("=" * 70)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in .env")
        return
    
    # Step 1: Create household
    print("\n📋 Step 1: Creating household profile...")
    create_household_profile("demo_family", "Demo Family", 45, 150.0, "Mediterranean, Indian")
    print("✅ Household created")
    
    # Step 2: Add members
    print("\n👨‍👩‍👦 Step 2: Adding family members...")
    add_family_member("demo_family", "Alice", 35, "vegetarian", "", "PCOS")
    add_family_member("demo_family", "Bob", 33, "", "nuts", "diabetes")
    add_family_member("demo_family", "Charlie", 8, "", "", "")
    print("✅ 3 family members added")
    
    # Step 3: View constraints
    print("\n🔍 Step 3: Household constraints:")
    constraints = get_household_constraints("demo_family")
    print(json.dumps(constraints, indent=2))
    
    # Step 4: Initialize orchestrator
    print("\n🤖 Step 4: Initializing 5-agent orchestrator...")
    orchestrator = create_orchestrator(api_key)
    print("✅ Orchestrator ready")
    print("   • Profile Manager")
    print("   • Recipe Generator")
    print("   • Nutrition Validator")
    print("   • Schedule Optimizer")
    print("   • Grocery Generator")
    
    # Step 5: Generate meal plan
    print("\n🍽️  Step 5: Generating 3-day meal plan...")
    print("Processing through all 5 agents...")
    
    result = await orchestrator.generate_meal_plan("demo_family", days=3)
    
    print("\n✅ COMPLETE!")
    print("=" * 70)
    print(result)
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
