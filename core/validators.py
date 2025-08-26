from django.core.exceptions import ValidationError


def validate_member_is_in_project(user, project):
    if user and not project.members.filter(pk=user.pk).exists():
        raise ValidationError("Assignee must be a member of the project.")
