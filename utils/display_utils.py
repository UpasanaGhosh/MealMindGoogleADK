"""Beautiful display utilities for MealMind output."""


def create_progress_bar(value: float, max_value: float, width: int = 20) -> str:
    """Create ASCII progress bar."""
    percentage = min(100, (value / max_value) * 100) if max_value > 0 else 0
    filled = int((percentage / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar} {percentage:.0f}%"


def create_box(title: str, width: int = 80) -> str:
    """Create decorative box around title."""
    return f"""
╔{'═' * (width-2)}╗
║{title.center(width-2)}║
╚{'═' * (width-2)}╝"""


def create_section_header(title: str, emoji: str = "📊") -> str:
    """Create section header with emoji."""
    return f"\n{emoji} {title}\n{'─' * 80}"


def format_currency(amount: float) -> str:
    """Format currency with color indicator."""
    return f"${amount:.2f}"


def format_status(condition: bool, yes_text: str = "Within limit", no_text: str = "Exceeds limit") -> str:
    """Format status with indicator."""
    return f"{'✅' if condition else '⚠️'} {yes_text if condition else no_text}"


def create_rating_stars(score: float, max_score: float = 100) -> str:
    """Create star rating from score."""
    stars = int((score / max_score) * 5)
    return "★" * stars + "☆" * (5 - stars) + f" ({score:.0f}/{max_score:.0f})"


def display_meal_plan_header(household_name: str, days: int):
    """Display beautiful header for meal plan."""
    header = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                   🍽️  MEALMIND MEAL PLAN GENERATOR                        ║
║                                                                            ║
║                     {household_name.center(52)}                     ║
║                     {f'{days}-Day Comprehensive Plan'.center(52)}                     ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
    return header


def display_day_header(day_number: int):
    """Display day header."""
    return f"\n{'─' * 80}\n📅 DAY {day_number}\n{'─' * 80}"


def display_meal_summary(meal_name: str, meal_type: str, time: int, cost: float, calories: float, protein: float):
    """Display meal summary in beautiful format."""
    return f"""
  {meal_type.upper()}: {meal_name}
  ├─ ⏱️  Time: {time} minutes
  ├─ 💵 Cost: ${cost:.2f}
  └─ 📊 Nutrition: {calories:.0f} cal | {protein:.0f}g protein"""


def display_budget_analysis(total_cost: float, budget: float):
    """Display budget analysis with progress bar."""
    within_budget = total_cost <= budget
    percentage = (total_cost / budget) * 100
    
    status = format_status(within_budget, "Within Budget", "Over Budget")
    progress = create_progress_bar(total_cost, budget)
    
    return f"""
{create_section_header("BUDGET ANALYSIS", "💰")}
{status}
Budget: {format_currency(budget)} | Spent: {format_currency(total_cost)}
{progress}
{"Savings: " + format_currency(budget - total_cost) if within_budget else "Overage: " + format_currency(total_cost - budget)}
"""


def display_optimization_summary(avg_time: float, target_time: float, reused_count: int, total_ingredients: int, score: float):
    """Display optimization analysis."""
    time_ok = avg_time <= target_time
    reuse_ratio = (reused_count / total_ingredients * 100) if total_ingredients > 0 else 0
    
    return f"""
{create_section_header("OPTIMIZATION ANALYSIS", "⚡")}
⏱️  Cooking Time: {format_status(time_ok)} - {avg_time:.0f} min/day (target: {target_time})
   {create_progress_bar(avg_time, target_time * 1.5)}

🔄 Ingredient Efficiency: {reused_count}/{total_ingredients} reused ({reuse_ratio:.0f}%)
   {create_progress_bar(reused_count, total_ingredients)}

📈 Overall Score: {create_rating_stars(score)}
"""


def display_member_preferences(member_name: str, favorites: List, dislikes: List, preferences: Dict):
    """Display member-specific preferences."""
    return f"""
👤 {member_name}:
   ⭐ Favorites: {len(favorites)} recipes
   ❌ Dislikes: {', '.join(dislikes) if dislikes else 'None'}
   💡 Preferences: {', '.join([f'{k}: {v}' for k, v in preferences.items()]) if preferences else 'None'}"""
