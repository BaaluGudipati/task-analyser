from django.test import TestCase
from datetime import date, timedelta
from .scoring import TaskScorer


class TaskScorerTestCase(TestCase):
    """Unit tests for the TaskScorer algorithm"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scorer = TaskScorer(strategy='smart_balance')
        self.today = date.today()
    
    def test_overdue_task_gets_highest_priority(self):
        """Test that overdue tasks receive maximum urgency score"""
        overdue_task = {
            'id': 1,
            'title': 'Overdue Task',
            'due_date': (self.today - timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 3,
            'importance': 5,
            'dependencies': []
        }
        
        normal_task = {
            'id': 2,
            'title': 'Future Task',
            'due_date': (self.today + timedelta(days=10)).strftime('%Y-%m-%d'),
            'estimated_hours': 3,
            'importance': 5,
            'dependencies': []
        }
        
        overdue_score, _ = self.scorer.calculate_score(overdue_task)
        normal_score, _ = self.scorer.calculate_score(normal_task)
        
        self.assertGreater(
            overdue_score, normal_score,
            "Overdue tasks should have higher priority than future tasks"
        )
    
    def test_importance_weighting(self):
        """Test that importance affects scoring correctly"""
        low_importance = {
            'id': 1,
            'title': 'Low Priority',
            'due_date': (self.today + timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 2,
            'importance': 2,
            'dependencies': []
        }
        
        high_importance = {
            'id': 2,
            'title': 'High Priority',
            'due_date': (self.today + timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 2,
            'importance': 10,
            'dependencies': []
        }
        
        low_score, _ = self.scorer.calculate_score(low_importance)
        high_score, _ = self.scorer.calculate_score(high_importance)
        
        self.assertGreater(
            high_score, low_score,
            "Higher importance tasks should score higher"
        )
    
    def test_quick_win_bonus(self):
        """Test that quick tasks get bonus points"""
        quick_task = {
            'id': 1,
            'title': 'Quick Task',
            'due_date': (self.today + timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 1,
            'importance': 5,
            'dependencies': []
        }
        
        long_task = {
            'id': 2,
            'title': 'Long Task',
            'due_date': (self.today + timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 8,
            'importance': 5,
            'dependencies': []
        }
        
        quick_score, explanation = self.scorer.calculate_score(quick_task)
        long_score, _ = self.scorer.calculate_score(long_task)
        
        self.assertGreater(
            quick_score, long_score,
            "Quick tasks should get bonus points"
        )
        self.assertIn('Quick win', explanation)
    
    def test_dependency_multiplier(self):
        """Test that tasks blocking others get higher priority"""
        blocking_task = {
            'id': 1,
            'title': 'Blocker',
            'due_date': (self.today + timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 2,
            'importance': 5,
            'dependencies': []
        }
        
        dependent_task = {
            'id': 2,
            'title': 'Dependent',
            'due_date': (self.today + timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 2,
            'importance': 5,
            'dependencies': [1]
        }
        
        regular_task = {
            'id': 3,
            'title': 'Regular',
            'due_date': (self.today + timedelta(days=5)).strftime('%Y-%m-%d'),
            'estimated_hours': 2,
            'importance': 5,
            'dependencies': []
        }
        
        all_tasks = [blocking_task, dependent_task, regular_task]
        
        blocking_score, explanation = self.scorer.calculate_score(blocking_task, all_tasks)
        regular_score, _ = self.scorer.calculate_score(regular_task, all_tasks)
        
        self.assertGreater(
            blocking_score, regular_score,
            "Tasks that block others should score higher"
        )
        self.assertIn('Unblocks', explanation)
    
    def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected"""
        tasks_with_cycle = [
            {'id': 1, 'dependencies': [2]},
            {'id': 2, 'dependencies': [3]},
            {'id': 3, 'dependencies': [1]},  # Creates cycle
        ]
        
        circular = self.scorer.detect_circular_dependencies(tasks_with_cycle)
        
        self.assertTrue(
            len(circular) > 0,
            "Circular dependencies should be detected"
        )
    
    def test_validation_missing_fields(self):
        """Test that validation catches missing required fields"""
        invalid_task = {
            'title': 'Incomplete Task',
            # Missing due_date, estimated_hours, importance
        }
        
        is_valid, error_msg = self.scorer.validate_task(invalid_task)
        
        self.assertFalse(is_valid, "Should reject task with missing fields")
        self.assertIn('Missing', error_msg)
    
    def test_validation_importance_range(self):
        """Test that importance is validated to be 1-10"""
        invalid_task = {
            'title': 'Invalid Importance',
            'due_date': self.today.strftime('%Y-%m-%d'),
            'estimated_hours': 2,
            'importance': 15,  # Invalid
            'dependencies': []
        }
        
        is_valid, error_msg = self.scorer.validate_task(invalid_task)
        
        self.assertFalse(is_valid, "Should reject importance outside 1-10 range")
        self.assertIn('1-10', error_msg)
    
    def test_strategy_fastest_wins(self):
        """Test fastest_wins strategy prioritizes speed"""
        scorer_fastest = TaskScorer(strategy='fastest_wins')
        
        quick_task = {
            'id': 1,
            'title': 'Quick',
            'due_date': (self.today + timedelta(days=10)).strftime('%Y-%m-%d'),
            'estimated_hours': 1,
            'importance': 3,
            'dependencies': []
        }
        
        important_but_slow = {
            'id': 2,
            'title': 'Slow but Important',
            'due_date': (self.today + timedelta(days=10)).strftime('%Y-%m-%d'),
            'estimated_hours': 8,
            'importance': 10,
            'dependencies': []
        }
        
        quick_score, _ = scorer_fastest.calculate_score(quick_task)
        slow_score, _ = scorer_fastest.calculate_score(important_but_slow)
        
        self.assertGreater(
            quick_score, slow_score,
            "In fastest_wins strategy, speed should trump importance"
        )
    
    def test_strategy_deadline_driven(self):
        """Test deadline_driven strategy prioritizes due dates"""
        scorer_deadline = TaskScorer(strategy='deadline_driven')
        
        urgent_task = {
            'id': 1,
            'title': 'Urgent',
            'due_date': (self.today + timedelta(days=1)).strftime('%Y-%m-%d'),
            'estimated_hours': 5,
            'importance': 3,
            'dependencies': []
        }
        
        important_but_later = {
            'id': 2,
            'title': 'Important Later',
            'due_date': (self.today + timedelta(days=30)).strftime('%Y-%m-%d'),
            'estimated_hours': 2,
            'importance': 10,
            'dependencies': []
        }
        
        urgent_score, _ = scorer_deadline.calculate_score(urgent_task)
        later_score, _ = scorer_deadline.calculate_score(important_but_later)
        
        self.assertGreater(
            urgent_score, later_score,
            "In deadline_driven strategy, urgency should dominate"
        )