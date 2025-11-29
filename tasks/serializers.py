from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    """
    Serializer for task data - converts between JSON and Python objects
    """
    id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=200)
    due_date = serializers.DateField(format='%Y-%m-%d')
    estimated_hours = serializers.IntegerField(min_value=1)
    importance = serializers.IntegerField(min_value=1, max_value=10)
    dependencies = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )
    
    # These fields are added by our algorithm
    priority_score = serializers.FloatField(required=False, read_only=True)
    explanation = serializers.CharField(required=False, read_only=True)


class TaskAnalysisRequestSerializer(serializers.Serializer):
    """
    Handles incoming request for task analysis
    """
    tasks = serializers.ListField(
        child=serializers.DictField()
    )
    strategy = serializers.ChoiceField(
        choices=['smart_balance', 'fastest_wins', 'high_impact', 'deadline_driven'],
        default='smart_balance',
        required=False
    )