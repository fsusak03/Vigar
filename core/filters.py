import datetime

import django_filters as df
from django.db.models import Q

from .models import Project, Task, TimeEntry


class ProjectFilter(df.FilterSet):
    search = df.CharFilter(
        method="filter_search", help_text="Search by project or client name (icontains)"
    )
    status = df.MultipleChoiceFilter(
        choices=Project.STATUS, help_text="Filter by one or more statuses"
    )
    client = df.NumberFilter(field_name="client_id", help_text="Filter by client id")
    member = df.NumberFilter(
        field_name="members__id", help_text="Filter by member user id"
    )
    start_date = df.DateFromToRangeFilter(
        help_text="Filter by start_date range (after..before)"
    )
    deadline = df.DateFromToRangeFilter(
        help_text="Filter by deadline range (after..before)"
    )
    ordering = df.OrderingFilter(
        fields=(
            ("name", "name"),
            ("created_at", "created_at"),
            ("start_date", "start_date"),
            ("deadline", "deadline"),
        ),
        field_labels={
            "name": "Name",
            "created_at": "Created at",
            "start_date": "Start date",
            "deadline": "Deadline",
        },
        help_text="Order results by one of the allowed fields",
    )

    class Meta:
        model = Project
        fields = [
            "search",
            "client",
            "status",
            "member",
            "start_date",
            "deadline",
            "ordering",
        ]

    # /**
    #  * filter_search
    #  * Filters projects by name or client name using icontains.
    #  *
    #  * @param queryset QuerySet[Project] incoming queryset
    #  * @param name str (unused)
    #  * @param value str search text; falsy returns queryset unchanged
    #  * @returns QuerySet[Project]
    #  */
    def filter_search(self, queryset, name, value):  # noqa: ARG002
        if not value:
            return queryset
        v = value.strip()
        return queryset.filter(Q(name__icontains=v) | Q(client__name__icontains=v))


class TaskFilter(df.FilterSet):
    project = df.NumberFilter(field_name="project_id", help_text="Filter by project id")
    assignee = df.NumberFilter(
        field_name="assignee_id", help_text="Filter by assignee user id"
    )
    status = df.MultipleChoiceFilter(
        choices=Task.STATUS, help_text="Filter by one or more statuses"
    )
    due_date = df.DateFromToRangeFilter(
        help_text="Filter by due_date range (after..before)"
    )
    has_assignee = df.BooleanFilter(
        method="filter_has_assignee",
        help_text="True for assigned tasks, False for unassigned",
    )
    is_overdue = df.BooleanFilter(
        method="filter_is_overdue",
        help_text="True to return overdue (due_date < today and not done)",
    )
    search = df.CharFilter(
        method="filter_search", help_text="Search by title or description (icontains)"
    )
    ordering = df.OrderingFilter(
        fields=(
            ("created_at", "created_at"),
            ("due_date", "due_date"),
            ("estimate_hours", "estimate_hours"),
            ("title", "title"),
        ),
        help_text="Order results by created_at, due_date, estimate_hours, or title",
    )

    class Meta:
        model = Task
        fields = [
            "project",
            "assignee",
            "status",
            "due_date",
            "has_assignee",
            "is_overdue",
            "search",
            "ordering",
        ]

    # /**
    #  * filter_has_assignee
    #  * Filters tasks by presence of an assignee.
    #  *
    #  * @param queryset QuerySet[Task]
    #  * @param name str (unused)
    #  * @param value bool|None True -> only assigned; False -> only
    #  *   unassigned; None -> unchanged
    #  * @returns QuerySet[Task]
    #  */
    def filter_has_assignee(self, queryset, name, value):  # noqa: ARG002
        if value is None:
            return queryset
        if value:
            return queryset.exclude(assignee__isnull=True)
        return queryset.filter(assignee__isnull=True)

    # /**
    #  * filter_is_overdue
    #  * Returns tasks overdue relative to today when value is True.
    #  * Overdue = due_date < today and status != 'done'.
    #  *
    #  * @param queryset QuerySet[Task]
    #  * @param name str (unused)
    #  * @param value bool when True filters to overdue; otherwise unchanged
    #  * @returns QuerySet[Task]
    #  */
    def filter_is_overdue(self, queryset, name, value):  # noqa: ARG002
        if value:
            today = datetime.date.today()
            return queryset.filter(due_date__lt=today).exclude(status__iexact="done")
        return queryset

    # /**
    #  * filter_search
    #  * Filters tasks by title or description using icontains.
    #  *
    #  * @param queryset QuerySet[Task]
    #  * @param name str (unused)
    #  * @param value str search text; falsy returns queryset unchanged
    #  * @returns QuerySet[Task]
    #  */
    def filter_search(self, queryset, name, value):  # noqa: ARG002
        if not value:
            return queryset
        v = value.strip()
        return queryset.filter(Q(title__icontains=v) | Q(description__icontains=v))


class TimeEntryFilter(df.FilterSet):
    user = df.NumberFilter(field_name="user_id", help_text="Filter by user id")
    task = df.NumberFilter(field_name="task_id", help_text="Filter by task id")
    project = df.NumberFilter(
        field_name="task__project_id", help_text="Filter by project id"
    )
    client = df.NumberFilter(
        field_name="task__project__client_id", help_text="Filter by client id"
    )
    date = df.DateFromToRangeFilter(help_text="Filter by date range (after..before)")
    hours_min = df.NumberFilter(
        field_name="hours", lookup_expr="gte", help_text="Minimum hours"
    )
    hours_max = df.NumberFilter(
        field_name="hours", lookup_expr="lte", help_text="Maximum hours"
    )
    search = df.CharFilter(
        method="filter_search", help_text="Search in note (icontains)"
    )
    ordering = df.OrderingFilter(
        fields=(
            ("date", "date"),
            ("hours", "hours"),
            ("created_at", "created_at"),
        ),
        help_text="Order results by date, hours, or created_at",
    )

    class Meta:
        model = TimeEntry
        fields = [
            "user",
            "task",
            "project",
            "client",
            "date",
            "hours_min",
            "hours_max",
            "search",
            "ordering",
        ]

    # /**
    #  * filter_search
    #  * Filters time entries by note using icontains.
    #  *
    #  * @param queryset QuerySet[TimeEntry]
    #  * @param name str (unused)
    #  * @param value str search text; falsy returns queryset unchanged
    #  * @returns QuerySet[TimeEntry]
    #  */
    def filter_search(self, queryset, name, value):  # noqa: ARG002
        if not value:
            return queryset
        return queryset.filter(note__icontains=value.strip())
