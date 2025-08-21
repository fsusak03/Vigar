import django_filters as df
from .models import Project, Task, TimeEntry

class ProjectFilter(df.FilterSet):
    status = df.CharFilter(lookup_expr="iexact")
    client = df.NumberFilter(field_name="client_id")
    class Meta:
        model = Project
        fields = ["client", "status"]

class TaskFilter(df.FilterSet):
    project = df.NumberFilter(field_name="project_id")
    assignee = df.NumberFilter(field_name="assignee_id")
    status = df.CharFilter(lookup_expr="iexact")
    due_date = df.DateFromToRangeFilter()
    class Meta:
        model = Task
        fields = ["project", "assignee", "status", "due_date"]

class TimeEntryFilter(df.FilterSet):
    user = df.NumberFilter(field_name="user_id")
    task = df.NumberFilter(field_name="task_id")
    date = df.DateFromToRangeFilter()
    class Meta:
        model = TimeEntry
        fields = ["user", "task", "date"]
