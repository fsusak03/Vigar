from django.db.models import Sum

from .models import Client, Project, Task, TimeEntry


def clients_qs():
    return Client.objects.all().order_by("name")


def projects_qs():
    return Project.objects.select_related("client").prefetch_related("members")


def tasks_qs():
    return Task.objects.select_related("project", "assignee", "project__client")


def time_entries_qs():
    return TimeEntry.objects.select_related(
        "task", "user", "task__project", "task__project__client"
    )


def total_hours_by_project(date_from=None, date_to=None):
    qs = time_entries_qs()
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return (
        qs.values("task__project", "task__project__name", "task__project__client__name")
        .annotate(total_hours=Sum("hours"))
        .order_by("-total_hours")
    )
