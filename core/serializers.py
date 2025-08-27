from django.contrib.auth import get_user_model
from rest_framework import serializers

from . import services as svc
from .models import Client, Project, Task, TimeEntry

User = get_user_model()


class UserBrief(serializers.ModelSerializer):
    # /**
    #  * UserBrief
    #  * Minimal user representation used in nested outputs.
    #  * @property {int} id
    #  * @property {string} username
    #  * @property {string} first_name
    #  * @property {string} last_name
    #  * @property {string} email
    #  */
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class ClientSerializer(serializers.ModelSerializer):
    # /**
    #  * ClientSerializer
    #  * Full representation of a client.
    #  * Uses all model fields.
    #  */
    class Meta:
        model = Client
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    # /**
    #  * ProjectSerializer
    #  * Project with nested read-only client and members, plus write-only ID
    #  * fields.
    #  * @field client          {ClientSerializer} (read-only)
    #  * @field client_id       {int} (write-only -> sets client)
    #  * @field members         {UserBrief[]} (read-only)
    #  * @field member_ids      {int[]} (write-only -> sets members)
    #  * create/update delegate to services for domain validation.
    #  */
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

    def create(self, validated_data):
        client = validated_data.pop("client")
        members = validated_data.pop("members", [])
        return svc.create_project(client=client, members=members, **validated_data)

    def update(self, instance, validated_data):
        members = validated_data.pop("members", None)
        instance = svc.update_project(instance, **validated_data)
        if members is not None:
            instance.members.set(members)
        return instance


class TaskSerializer(serializers.ModelSerializer):
    # /**
    #  * TaskSerializer
    #  * Task with write-only project_id and assignee_id, read-only nested
    #  * assignee. create() and update() call services for membership checks and
    #  * reassignment.
    #  */
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

    def create(self, validated_data):
        project = validated_data.pop("project")
        assignee = validated_data.pop("assignee", None)
        return svc.create_task(project=project, assignee=assignee, **validated_data)

    def update(self, instance, validated_data):
        if "assignee" in validated_data:
            assignee = validated_data.pop("assignee")
            instance = svc.reassign_task(instance, assignee=assignee)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class TimeEntrySerializer(serializers.ModelSerializer):
    # /**
    #  * TimeEntrySerializer
    #  * Time entry with write-only task_id and user_id, read-only nested user.
    #  * create() calls services.log_time for validation and permissions.
    #  */
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

    def create(self, validated_data):
        task = validated_data.pop("task")
        user = validated_data.pop("user")
        return svc.log_time(task=task, user=user, **validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    # /**
    #  * RegisterSerializer
    #  * Validates and creates a new user with password confirmation and
    #  * email uniqueness.
    #  * @field password  {string} write-only, min_length=8
    #  * @field password2 {string} write-only, must match password
    #  * @field email     {Email}  required, unique (case-insensitive)
    #  */
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
