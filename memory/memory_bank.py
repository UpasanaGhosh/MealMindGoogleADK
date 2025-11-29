"""Enhanced Memory Bank - Per-member preference tracking."""
import json
from typing import Dict, List, Optional
from datetime import datetime


class MemoryBank:
    """Long-term memory with per-member preference tracking."""
    
    def __init__(self):
        """Initialize enhanced memory bank."""
        # Household-level
        self.meal_history = {}  # household_id -> [meal_plans]
        self.household_preferences = {}  # household_id -> shared_preferences
        
        # Per-member tracking
        self.member_favorites = {}  # household_id -> {member_name -> [recipes]}
        self.member_dislikes = {}  # household_id -> {member_name -> [ingredients]}
        self.member_preferences = {}  # household_id -> {member_name -> preferences}
        self.member_health_history = {}  # household_id -> {member_name -> health_data}
    
    # ============================================================================
    # PER-MEMBER FAVORITES
    # ============================================================================
    
    def add_member_favorite(self, household_id: str, member_name: str, recipe: Dict):
        """Add favorite recipe for specific member."""
        if household_id not in self.member_favorites:
            self.member_favorites[household_id] = {}
        
        if member_name not in self.member_favorites[household_id]:
            self.member_favorites[household_id][member_name] = []
        
        # Avoid duplicates
        if not any(r.get('name') == recipe.get('name') for r in self.member_favorites[household_id][member_name]):
            self.member_favorites[household_id][member_name].append({
                **recipe,
                "favorited_at": datetime.now().isoformat(),
                "favorited_by": member_name
            })
    
    def get_member_favorites(self, household_id: str, member_name: str) -> List[Dict]:
        """Get favorite recipes for specific member."""
        if household_id in self.member_favorites:
            return self.member_favorites[household_id].get(member_name, [])
        return []
    
    def get_all_member_favorites(self, household_id: str) -> Dict[str, List]:
        """Get favorites for all members."""
        return self.member_favorites.get(household_id, {})
    
    # ============================================================================
    # PER-MEMBER DISLIKES
    # ============================================================================
    
    def add_member_dislike(self, household_id: str, member_name: str, ingredient: str):
        """Add disliked ingredient for specific member."""
        if household_id not in self.member_dislikes:
            self.member_dislikes[household_id] = {}
        
        if member_name not in self.member_dislikes[household_id]:
            self.member_dislikes[household_id][member_name] = []
        
        ingredient_lower = ingredient.lower()
        if ingredient_lower not in [d.lower() for d in self.member_dislikes[household_id][member_name]]:
            self.member_dislikes[household_id][member_name].append(ingredient)
    
    def get_member_dislikes(self, household_id: str, member_name: str) -> List[str]:
        """Get disliked ingredients for specific member."""
        if household_id in self.member_dislikes:
            return self.member_dislikes[household_id].get(member_name, [])
        return []
    
    def get_all_member_dislikes(self, household_id: str) -> Dict[str, List]:
        """Get dislikes for all members."""
        return self.member_dislikes.get(household_id, {})
    
    def get_household_dislikes(self, household_id: str) -> List[str]:
        """Get ALL dislikes across household (for safe meal planning)."""
        all_dislikes = []
        if household_id in self.member_dislikes:
            for member_dislikes in self.member_dislikes[household_id].values():
                all_dislikes.extend(member_dislikes)
        return list(set(all_dislikes))
    
    # ============================================================================
    # PER-MEMBER PREFERENCES
    # ============================================================================
    
    def update_member_preferences(self, household_id: str, member_name: str, preferences: Dict):
        """Update preferences for specific member."""
        if household_id not in self.member_preferences:
            self.member_preferences[household_id] = {}
        
        if member_name not in self.member_preferences[household_id]:
            self.member_preferences[household_id][member_name] = {}
        
        self.member_preferences[household_id][member_name].update(preferences)
    
    def get_member_preferences(self, household_id: str, member_name: str) -> Dict:
        """Get preferences for specific member."""
        if household_id in self.member_preferences:
            return self.member_preferences[household_id].get(member_name, {})
        return {}
    
    def get_all_member_preferences(self, household_id: str) -> Dict[str, Dict]:
        """Get preferences for all members."""
        return self.member_preferences.get(household_id, {})
    
    # ============================================================================
    # MEAL HISTORY (Household-level)
    # ============================================================================
    
    def store_meal_plan(self, household_id: str, meal_plan: Dict):
        """Store meal plan in history."""
        if household_id not in self.meal_history:
            self.meal_history[household_id] = []
        
        self.meal_history[household_id].append({
            "plan": meal_plan,
            "created_at": datetime.now().isoformat()
        })
        
        # Keep only last 10 plans
        if len(self.meal_history[household_id]) > 10:
            self.meal_history[household_id] = self.meal_history[household_id][-10:]
    
    def get_meal_history(self, household_id: str, limit: int = 5) -> List[Dict]:
        """Get recent meal plans."""
        history = self.meal_history.get(household_id, [])
        return history[-limit:] if len(history) > limit else history
    
    # ============================================================================
    # MEMORY CONTEXT
    # ============================================================================
    
    def get_memory_context(self, household_id: str) -> Dict:
        """Get complete memory context with per-member data."""
        return {
            "household_favorites": self.get_all_member_favorites(household_id),
            "household_dislikes": self.get_all_member_dislikes(household_id),
            "all_dislikes": self.get_household_dislikes(household_id),  # Combined for safety
            "member_preferences": self.get_all_member_preferences(household_id),
            "recent_plans": self.get_meal_history(household_id, limit=3)
        }
    
    def get_member_profile_summary(self, household_id: str, member_name: str) -> Dict:
        """Get complete profile for one member."""
        return {
            "name": member_name,
            "favorites": self.get_member_favorites(household_id, member_name),
            "dislikes": self.get_member_dislikes(household_id, member_name),
            "preferences": self.get_member_preferences(household_id, member_name)
        }


# Global instance
memory_bank = MemoryBank()
