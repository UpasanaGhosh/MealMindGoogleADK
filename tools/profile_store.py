"""Profile store tools for household management."""
from typing import Dict

# Global storage for household profiles
HOUSEHOLD_PROFILES = {}


def create_household_profile(
    household_id: str,
    household_name: str,
    cooking_time_max: int = 45,
    budget_weekly: float = 150.0,
    cuisine_preferences: str = ""
) -> Dict:
    """Create a new household profile.
    
    Args:
        household_id: Unique household identifier
        household_name: Name of the household
        cooking_time_max: Maximum cooking time per day in minutes
        budget_weekly: Weekly grocery budget
        cuisine_preferences: Comma-separated list of preferred cuisines
    
    Returns:
        Created household profile
    """
    cuisines = [c.strip() for c in cuisine_preferences.split(",") if c.strip()]
    
    HOUSEHOLD_PROFILES[household_id] = {
        "household_id": household_id,
        "household_name": household_name,
        "cooking_time_max": cooking_time_max,
        "budget_weekly": budget_weekly,
        "cuisine_preferences": cuisines,
        "members": []
    }
    
    return HOUSEHOLD_PROFILES[household_id]


def add_family_member(
    household_id: str,
    name: str,
    age: int,
    dietary_restrictions: str = "",
    allergies: str = "",
    health_conditions: str = ""
) -> Dict:
    """Add a family member to household.
    
    Args:
        household_id: Household identifier
        name: Member name
        age: Member age
        dietary_restrictions: Comma-separated dietary restrictions
        allergies: Comma-separated allergies
        health_conditions: Comma-separated health conditions
    
    Returns:
        Created member profile
    """
    if household_id not in HOUSEHOLD_PROFILES:
        return {"error": "Household not found"}
    
    member = {
        "name": name,
        "age": age,
        "dietary_restrictions": [r.strip() for r in dietary_restrictions.split(",") if r.strip()],
        "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
        "health_conditions": [h.strip() for h in health_conditions.split(",") if h.strip()]
    }
    
    HOUSEHOLD_PROFILES[household_id]["members"].append(member)
    return member


def get_household_constraints(household_id: str) -> Dict:
    """Get all dietary constraints for a household.
    
    Args:
        household_id: Household identifier
    
    Returns:
        Aggregated constraints from all members
    """
    if household_id not in HOUSEHOLD_PROFILES:
        return {"error": "Household not found"}
    
    profile = HOUSEHOLD_PROFILES[household_id]
    all_restrictions = []
    all_allergies = []
    all_conditions = []
    
    for member in profile["members"]:
        all_restrictions.extend(member["dietary_restrictions"])
        all_allergies.extend(member["allergies"])
        all_conditions.extend(member["health_conditions"])
    
    return {
        "household_id": household_id,
        "dietary_restrictions": list(set(all_restrictions)),
        "allergies": list(set(all_allergies)),
        "health_conditions": list(set(all_conditions)),
        "cooking_time_max": profile["cooking_time_max"],
        "budget_weekly": profile["budget_weekly"],
        "cuisine_preferences": profile["cuisine_preferences"],
        "member_count": len(profile["members"]),
        "members": profile["members"]
    }
