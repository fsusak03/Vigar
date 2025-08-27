from typing import Any, Dict, List, Optional, no_type_check

from django.db.models import Count, QuerySet, Sum

from .models import Client, Project, Task, TimeEntry


# Base querysets
def clients_qs() -> QuerySet[Client]:
    return Client.objects.all().order_by("name")


def projects_qs() -> QuerySet[Project]:
    return Project.objects.select_related("client").prefetch_related("members")


def tasks_qs() -> QuerySet[Task]:
    return Task.objects.select_related("project", "assignee", "project__client")


def time_entries_qs() -> QuerySet[TimeEntry]:
    return TimeEntry.objects.select_related(
        "task", "user", "task__project", "task__project__client"
    )


def get_client(client_id: int) -> Client:
    return clients_qs().get(pk=client_id)


def get_project(project_id: int) -> Project:
    return projects_qs().get(pk=project_id)


def get_task(task_id: int) -> Task:
    return tasks_qs().get(pk=task_id)


# Scopes by user
def projects_for_user(user: Any) -> QuerySet[Project]:
    """Projects where the user is a member.

    Accepts any user-like object with an id; filters via members__id for
    better typing compatibility.
    """
    return projects_qs().filter(members__id=getattr(user, "id", user))


def tasks_for_user(user: Any) -> QuerySet[Task]:
    """Tasks assigned to the user.

    Filters via assignee_id to avoid strict type coupling.
    """
    return tasks_qs().filter(assignee_id=getattr(user, "id", user))


def time_entries_for_user(
    user: Any,
    *,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> QuerySet[TimeEntry]:
    qs = time_entries_qs().filter(user_id=getattr(user, "id", user))
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return qs


def tasks_for_project(project_id: int) -> QuerySet[Task]:
    return tasks_qs().filter(project_id=project_id)


def time_entries_for_project(
    project_id: int, *, date_from: Optional[str] = None, date_to: Optional[str] = None
) -> QuerySet[TimeEntry]:
    qs = time_entries_qs().filter(task__project_id=project_id)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return qs


# Reports/aggregations
@no_type_check
def total_hours_by_project(
    date_from: Optional[str] = None, date_to: Optional[str] = None
) -> List[Dict[str, Any]]:
    qs = time_entries_qs()
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return list(
        qs.values("task__project", "task__project__name", "task__project__client__name")
        .annotate(total_hours=Sum("hours"))
        .order_by("-total_hours")
    )


@no_type_check
def total_hours_by_user(
    date_from: Optional[str] = None, date_to: Optional[str] = None
) -> List[Dict[str, Any]]:
    qs = time_entries_qs()
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return list(
        qs.values("user", "user__username")
        .annotate(total_hours=Sum("hours"))
        .order_by("-total_hours")
    )


@no_type_check
def task_counts_by_status(project_id: Optional[int] = None) -> List[Dict[str, Any]]:
    qs = tasks_qs()
    if project_id:
        qs = qs.filter(project_id=project_id)
    return list(qs.values("status").annotate(count=Count("id")).order_by("status"))
