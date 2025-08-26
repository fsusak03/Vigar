from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Client, Project, Task, TimeEntry

User = get_user_model()


class UserBrief(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    client_id = serializers.PrimaryKeyRelatedField(
        source="client", queryset=Client.objects.all(), write_only=True
    )
    members = UserBrief(many=True, read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(
        source="members",
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "start_date",
            "deadline",
            "status",
            "client",
            "client_id",
            "members",
            "member_ids",
            "created_at",
        ]


class TaskSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(
        source="project", queryset=Project.objects.all(), write_only=True
    )
    assignee = UserBrief(read_only=True)
    assignee_id = serializers.PrimaryKeyRelatedField(
        source="assignee",
        queryset=User.objects.all(),
        write_only=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "estimate_hours",
            "due_date",
            "project_id",
            "assignee",
            "assignee_id",
            "created_at",
        ]


class TimeEntrySerializer(serializers.ModelSerializer):
    task_id = serializers.PrimaryKeyRelatedField(
        source="task", queryset=Task.objects.all(), write_only=True
    )
    user = UserBrief(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all(), write_only=True
    )

    class Meta:
        model = TimeEntry
        fields = [
            "id",
            "date",
            "hours",
            "note",
            "task_id",
            "user",
            "user_id",
            "created_at",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password2"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password2"):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        attrs.pop("password2", None)
        email = attrs.get("email")
        if email:
            email_norm = email.strip().lower()
            if User.objects.filter(email__iexact=email_norm).exists():
                raise serializers.ValidationError(
                    {"email": "A user with that email already exists."}
                )
            attrs["email"] = email_norm
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user
