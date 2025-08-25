from django.db import transaction
from .models import Project, Task, TimeEntry
from .validators import validate_member_is_in_project

@transaction.atomic
def add_project_member(project: Project, user):
    project.members.add(user)
    return project

@transaction.atomic
def create_task(*, project: Project, title: str, assignee=None, **kwargs) -> Task:
    if assignee:
        validate_member_is_in_project(assignee, project)
    return Task.objects.create(project=project, title=title, assignee=assignee, **kwargs)

@transaction.atomic
def log_time(*, task: Task, user, date, hours, note=None) -> TimeEntry:
    return TimeEntry.objects.create(task=task, user=user, date=date, hours=hours, note=note)
