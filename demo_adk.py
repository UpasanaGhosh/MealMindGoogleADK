"""Demo script for ADK-based MealMind implementation."""
import os
import json
from dotenv import load_dotenv
from orchestrator_adk import create_adk_orchestrator
from tools.family_profile_store import profile_store

# Load environment variables
load_dotenv()

def setup_demo_household():
    """Set up demo household profile."""
    household_id = "demo_family"
    
    # Create demo profile
    profile_store.create_household_profile(
        household_id=household_id,
        household_name="Demo Family",
        members=[
            {
                "name": "Parent 1",
                "age": 35,
                "dietary_restrictions": ["vegetarian"],
                "allergies": [],
                "health_goals": ["weight_management"]
            },
            {
                "name": "Parent 2", 
                "age": 33,
                "dietary_restrictions": [],
                "allergies": ["nuts"],
                "health_goals": ["muscle_gain"]
            },
            {
                "name": "Child 1",
                "age": 8,
                "dietary_restrictions": [],
                "allergies": [],
                "health_goals": ["healthy_growth"]
            }
        ],
        budget_per_week=150.0,
        preferred_cuisines=["Mediterranean", "Indian", "Mexican"],
        cooking_skill_level="intermediate",
        available_time_weekday=45,
        available_time_weekend=90
    )
    
    return household_id

def main():
    """Run ADK demo."""
    print("🚀 MealMind ADK Demo Starting...")
    print("="*50)
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        print("Please set your Google API key in .env file")
        return
    
    try:
        # 1. Setup demo household
        print("📋 Setting up demo household...")
        household_id = setup_demo_household()
        print(f"✅ Demo household created: {household_id}")
        
        # 2. Initialize ADK orchestrator
        print("\n🔧 Initializing ADK orchestrator...")
        orchestrator = create_adk_orchestrator(api_key=api_key)
        print("✅ ADK orchestrator initialized successfully")
        print(f"   - Agent: {orchestrator.recipe_agent.agent.name}")
        print(f"   - Runner: {type(orchestrator.runner).__name__}")
        print(f"   - Session Service: {type(orchestrator.session_service).__name__}")
        print(f"   - App: {orchestrator.app.app_name}")
        
        # 3. Generate meal plan
        print("\n🍽️  Generating 3-day meal plan...")
        
        preferences = {
            "focus": "healthy, family-friendly meals",
            "dietary_style": "vegetarian-friendly with some meat",
            "budget_conscious": True,
            "prep_time_limit": "45 minutes weekdays, 90 minutes weekends"
        }
        
        result = orchestrator.generate_meal_plan(
            household_id=household_id,
            preferences=preferences,
            num_days=3
        )
        
        # 4. Display results
        print("\n📊 Results:")
        print("-" * 30)
        
        if result["status"] == "success":
            print("✅ Meal plan generated successfully!")
            print(f"   - Session ID: {result['session_id']}")
            print(f"   - Household: {result['household_id']}")
            
            # Pretty print meal plan
            meal_plan = result["meal_plan"]
            print(f"\n📝 Generated Response:")
            print(json.dumps(meal_plan, indent=2)[:1000] + "..." if len(str(meal_plan)) > 1000 else json.dumps(meal_plan, indent=2))
            
        else:
            print("❌ Failed to generate meal plan:")
            print(f"   Error: {result['error']}")
        
        # 5. Show session info
        print(f"\n📜 Session History:")
        history = orchestrator.get_session_history(result['session_id'])
        print(f"   - Events in session: {len(history)}")
        
        print("\n🎉 ADK Demo completed successfully!")
        print("="*50)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\n💡 This likely means google-adk is not installed.")
        print("   Run: pip install google-adk")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"   Error type: {type(e).__name__}")


if __name__ == "__main__":
    main()
