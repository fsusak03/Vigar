from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Client(models.Model):
    name = models.CharField(max_length=120, unique=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self): return self.name

class Project(models.Model):
    STATUS = [("active","Active"),("on_hold","On Hold"),("completed","Completed")]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS, default="active")
    members = models.ManyToManyField(User, blank=True, related_name="project_memberships")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("client", "name")
        ordering = ["client__name", "name"]

    def __str__(self): return f"{self.client} • {self.name}"

class Task(models.Model):
    STATUS = [("todo","To Do"),("in_progress","In Progress"),("done","Done")]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True, null=True)
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    status = models.CharField(max_length=20, choices=STATUS, default="todo")
    estimate_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self): return self.title

class TimeEntry(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="time_entries")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="time_entries")
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    note = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
