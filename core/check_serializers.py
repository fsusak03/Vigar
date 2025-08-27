from rest_framework import serializers


class UserHoursReportSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    total_hours = serializers.DecimalField(max_digits=10, decimal_places=2)


class TaskStatusCountSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()


class ProjectHoursReportSerializer(serializers.Serializer):
    project_id = serializers.IntegerField()
    project_name = serializers.CharField()
    client_name = serializers.CharField()
    total_hours = serializers.DecimalField(max_digits=10, decimal_places=2)
