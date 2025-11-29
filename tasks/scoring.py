from datetime import datetime, date
from typing import List, Dict, Any
import math

class TaskScorer:
    """
    Intelligent task scoring system that balances multiple factors.
    
    Scoring Philosophy:
    - Overdue tasks get exponential penalty (can't ignore them!)
    - Importance is weighted heavily (user knows what matters)
    - Quick wins get bonus (momentum matters)
    - Dependencies create multiplier effect (unblock others)
    """
    
    def __init__(self, strategy='smart_balance'):
        self.strategy = strategy
        
    def calculate_score(self, task: Dict[str, Any], all_tasks: List[Dict] = None) -> tuple:
        """
        Calculate priority score for a single task.
        Returns: (score, explanation)
        """
        if all_tasks is None:
            all_tasks = []
            
        score = 0
        reasons = []
        
        # Parse due date
        if isinstance(task.get('due_date'), str):
            due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
        else:
            due_date = task.get('due_date')
        
        # Get other fields with defaults
        importance = task.get('importance', 5)
        estimated_hours = task.get('estimated_hours', 1)
        dependencies = task.get('dependencies', [])
        task_id = task.get('id', 0)
        
        # Strategy-based scoring
        if self.strategy == 'fastest_wins':
            score = self._calculate_fastest_wins(estimated_hours, importance, reasons)
        elif self.strategy == 'high_impact':
            score = self._calculate_high_impact(importance, due_date, reasons)
        elif self.strategy == 'deadline_driven':
            score = self._calculate_deadline_driven(due_date, importance, reasons)
        else:  # smart_balance
            score = self._calculate_smart_balance(
                due_date, importance, estimated_hours, 
                dependencies, all_tasks, task_id, reasons
            )
        
        explanation = " | ".join(reasons)
        return round(score, 2), explanation
    
    def _calculate_smart_balance(self, due_date, importance, estimated_hours, 
                                 dependencies, all_tasks, task_id, reasons):
        """The sophisticated balanced algorithm"""
        score = 0
        today = date.today()
        days_until_due = (due_date - today).days
        
        # 1. URGENCY SCORING (0-100 points)
        if days_until_due < 0:
            # Overdue: exponential penalty
            overdue_days = abs(days_until_due)
            urgency_score = 100 + (overdue_days ** 1.5)
            reasons.append(f"⚠️ OVERDUE by {overdue_days} days")
        elif days_until_due == 0:
            urgency_score = 95
            reasons.append("🔥 Due TODAY")
        elif days_until_due <= 2:
            urgency_score = 80
            reasons.append(f"⏰ Due in {days_until_due} days")
        elif days_until_due <= 7:
            urgency_score = 50
            reasons.append(f"📅 Due this week")
        else:
            # Diminishing urgency for far-away tasks
            urgency_score = max(10, 50 - (days_until_due - 7) * 2)
            reasons.append(f"📆 Due in {days_until_due} days")
        
        score += urgency_score
        
        # 2. IMPORTANCE WEIGHTING (0-80 points)
        # Scale: 1-10 → 8-80 points
        importance_score = importance * 8
        score += importance_score
        reasons.append(f"💎 Importance: {importance}/10")
        
        # 3. EFFORT-BASED BONUS (Quick Wins)
        if estimated_hours <= 1:
            effort_bonus = 25
            reasons.append("⚡ Quick win (≤1hr)")
        elif estimated_hours <= 2:
            effort_bonus = 15
            reasons.append("✨ Fast task (≤2hrs)")
        elif estimated_hours <= 4:
            effort_bonus = 5
        else:
            effort_bonus = -5  # Slight penalty for long tasks
            reasons.append(f"⏳ Long task ({estimated_hours}hrs)")
        
        score += effort_bonus
        
        # 4. DEPENDENCY MULTIPLIER
        # Check if OTHER tasks depend on THIS task (i.e., this task blocks others)
        blocking_count = sum(
            1 for t in all_tasks 
            if task_id in t.get('dependencies', [])
        )
        
        if blocking_count > 0:
            dependency_bonus = blocking_count * 20
            score += dependency_bonus
            reasons.append(f"🔓 Unblocks {blocking_count} task(s)")
        
        return score
    
    def _calculate_fastest_wins(self, estimated_hours, importance, reasons):
        """Prioritize quick tasks"""
        score = 0
        
        # Heavy weighting on speed
        if estimated_hours <= 1:
            score += 100
            reasons.append("⚡ Ultra-fast (<1hr)")
        elif estimated_hours <= 2:
            score += 70
            reasons.append("✨ Fast (1-2hrs)")
        elif estimated_hours <= 4:
            score += 40
        else:
            score += 10
            
        # Still consider importance but lower weight
        score += importance * 3
        reasons.append(f"Importance: {importance}/10")
        
        return score
    
    def _calculate_high_impact(self, importance, due_date, reasons):
        """Prioritize importance above all"""
        score = importance * 15
        reasons.append(f"💎 High Impact: {importance}/10")
        
        # Minor urgency consideration
        days_until_due = (due_date - date.today()).days
        if days_until_due < 0:
            score += 30
            reasons.append("Also overdue")
        elif days_until_due <= 3:
            score += 15
            
        return score
    
    def _calculate_deadline_driven(self, due_date, importance, reasons):
        """Prioritize by deadline"""
        today = date.today()
        days_until_due = (due_date - today).days
        
        if days_until_due < 0:
            score = 200 + abs(days_until_due) * 10
            reasons.append(f"⚠️ OVERDUE by {abs(days_until_due)} days")
        elif days_until_due == 0:
            score = 180
            reasons.append("🔥 Due TODAY")
        elif days_until_due <= 7:
            score = 150 - (days_until_due * 10)
            reasons.append(f"⏰ Due in {days_until_due} days")
        else:
            score = max(20, 100 - days_until_due)
            reasons.append(f"📅 {days_until_due} days away")
        
        # Add importance as tie-breaker
        score += importance * 2
        
        return score
    
    def detect_circular_dependencies(self, tasks: List[Dict]) -> List[str]:
        """
        Detect circular dependencies using depth-first search.
        Returns list of task IDs involved in cycles.
        """
        def has_cycle(task_id, visited, rec_stack, task_map):
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = task_map.get(task_id)
            if task:
                for dep_id in task.get('dependencies', []):
                    if dep_id not in visited:
                        if has_cycle(dep_id, visited, rec_stack, task_map):
                            return True
                    elif dep_id in rec_stack:
                        return True
            
            rec_stack.remove(task_id)
            return False
        
        # Build task map
        task_map = {t.get('id', i): t for i, t in enumerate(tasks)}
        
        visited = set()
        circular = []
        
        for task_id in task_map.keys():
            if task_id not in visited:
                rec_stack = set()
                if has_cycle(task_id, visited, rec_stack, task_map):
                    circular.append(str(task_id))
        
        return circular
    
    def validate_task(self, task: Dict) -> tuple:
        """
        Validate task data and return (is_valid, error_message)
        """
        required_fields = ['title', 'due_date', 'estimated_hours', 'importance']
        
        for field in required_fields:
            if field not in task or task[field] is None:
                return False, f"Missing required field: {field}"
        
        # Validate importance range
        importance = task.get('importance')
        if not (1 <= importance <= 10):
            return False, f"Importance must be between 1-10, got {importance}"
        
        # Validate estimated hours
        estimated_hours = task.get('estimated_hours')
        if estimated_hours <= 0:
            return False, f"Estimated hours must be positive, got {estimated_hours}"
        
        # Validate date format
        try:
            if isinstance(task['due_date'], str):
                datetime.strptime(task['due_date'], '%Y-%m-%d')
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD"
        
        return True, ""