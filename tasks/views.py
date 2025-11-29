from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .scoring import TaskScorer
from .serializers import TaskSerializer, TaskAnalysisRequestSerializer


@api_view(['POST'])
def analyze_tasks(request):
    """
    POST /api/tasks/analyze/
    
    Accept a list of tasks and return them sorted by priority score.
    
    Request body:
    {
        "tasks": [...],
        "strategy": "smart_balance"  // optional
    }
    """
    # Validate input
    request_serializer = TaskAnalysisRequestSerializer(data=request.data)
    
    if not request_serializer.is_valid():
        return Response({
            'error': 'Invalid request format',
            'details': request_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    tasks = request_serializer.validated_data['tasks']
    strategy = request_serializer.validated_data.get('strategy', 'smart_balance')
    
    # Initialize scorer with chosen strategy
    scorer = TaskScorer(strategy=strategy)
    
    # Validate each task
    validated_tasks = []
    errors = []
    
    for idx, task in enumerate(tasks):
        is_valid, error_msg = scorer.validate_task(task)
        if not is_valid:
            errors.append(f"Task {idx + 1}: {error_msg}")
        else:
            # Add ID if not present
            if 'id' not in task:
                task['id'] = idx + 1
            validated_tasks.append(task)
    
    if errors and not validated_tasks:
        return Response({
            'error': 'All tasks have validation errors',
            'details': errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check for circular dependencies
    circular_deps = scorer.detect_circular_dependencies(validated_tasks)
    
    # Calculate scores for all tasks
    scored_tasks = []
    for task in validated_tasks:
        score, explanation = scorer.calculate_score(task, validated_tasks)
        task_with_score = {
            **task,
            'priority_score': score,
            'explanation': explanation
        }
        scored_tasks.append(task_with_score)
    
    # Sort by priority score (highest first)
    scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
    
    # Prepare response
    response_data = {
        'tasks': scored_tasks,
        'strategy_used': strategy,
        'total_tasks': len(scored_tasks),
    }
    
    if circular_deps:
        response_data['warnings'] = {
            'circular_dependencies': circular_deps,
            'message': 'Some tasks have circular dependencies'
        }
    
    if errors:
        response_data['validation_errors'] = errors
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def suggest_tasks(request):
    """
    POST /api/tasks/suggest/
    
    Return the top 3 tasks the user should work on today,
    with explanations for why each was chosen.
    
    Same request format as analyze_tasks.
    """
    # Validate input
    request_serializer = TaskAnalysisRequestSerializer(data=request.data)
    
    if not request_serializer.is_valid():
        return Response({
            'error': 'Invalid request format',
            'details': request_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    tasks = request_serializer.validated_data['tasks']
    strategy = request_serializer.validated_data.get('strategy', 'smart_balance')
    
    # Initialize scorer with chosen strategy
    scorer = TaskScorer(strategy=strategy)
    
    # Validate and score tasks
    validated_tasks = []
    for idx, task in enumerate(tasks):
        is_valid, error_msg = scorer.validate_task(task)
        if is_valid:
            if 'id' not in task:
                task['id'] = idx + 1
            validated_tasks.append(task)
    
    if not validated_tasks:
        return Response({
            'error': 'No valid tasks provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate scores for all tasks
    scored_tasks = []
    for task in validated_tasks:
        score, explanation = scorer.calculate_score(task, validated_tasks)
        task_with_score = {
            **task,
            'priority_score': score,
            'explanation': explanation
        }
        scored_tasks.append(task_with_score)
    
    # Sort by priority score (highest first)
    scored_tasks.sort(key=lambda x: x['priority_score'], reverse=True)
    
    # Get top 3
    top_tasks = scored_tasks[:3]
    
    # Add ranking and enhanced explanations
    suggestions = []
    for rank, task in enumerate(top_tasks, 1):
        suggestion = {
            'rank': rank,
            'task': {
                'id': task['id'],
                'title': task['title'],
                'due_date': task['due_date'],
                'estimated_hours': task['estimated_hours'],
                'importance': task['importance']
            },
            'priority_score': task['priority_score'],
            'why_this_task': task['explanation'],
            'recommendation': _generate_recommendation(rank, task, strategy)
        }
        suggestions.append(suggestion)
    
    return Response({
        'suggestions': suggestions,
        'strategy_used': strategy,
        'message': f'Top 3 tasks to work on today (using {strategy} strategy)'
    }, status=status.HTTP_200_OK)

def _generate_recommendation(rank, task, strategy):
    """Generate human-readable recommendation"""
    if rank == 1:
        return f"🎯 START HERE: '{task['title']}' is your highest priority task right now."
    elif rank == 2:
        return f"⭐ NEXT UP: After completing your top task, move to '{task['title']}'."
    else:
        return f"✅ THEN: '{task['title']}' should be tackled third to maintain momentum."


@api_view(['GET'])
def health_check(request):
    """Simple endpoint to verify API is running"""
    return Response({
        'status': 'healthy',
        'message': 'Task Analyzer API is running'
    })