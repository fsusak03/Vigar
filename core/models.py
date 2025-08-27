from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


# /**
#  * Client
#  * Represents a customer that owns one or more projects.
#  * @property {int} id - Primary key.
#  * @property {string} name - Unique client name (max_length=120).
#  * @property {string|null} contact_email - Optional contact email.
#  * @property {string|null} contact_phone - Optional contact phone.
#  * @property {string|null} note - Optional notes about the client.
#  * @property {datetime} created_at - Creation timestamp (auto_now_add).
#  * @relation {Project[]} projects - Reverse FK from Project.
#  */
class Client(models.Model):
    name = models.CharField(max_length=120, unique=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


# /**
#  * Project
#  * A project belongs to a client and can have many members and tasks.
#  * @property {int} id - Primary key.
#  * @property {Client} client - Owning client (FK).
#  * @property {string} name - Project name (unique per client, max_length=150).
#  * @property {string|null} description - Optional description.
#  * @property {date|null} start_date - Optional start date.
#  * @property {date|null} deadline - Optional deadline.
#  * @property {"active"|"on_hold"|"completed"} status - Project status.
#  * @property {User[]} members - Many-to-many project members.
#  * @property {datetime} created_at - Creation timestamp (auto_now_add).
#  * @relation {Task[]} tasks - Reverse FK from Task.
#  */
class Project(models.Model):
    STATUS = [("active", "Active"), ("on_hold", "On Hold"), ("completed", "Completed")]
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS, default="active")
    members = models.ManyToManyField(
        User, blank=True, related_name="project_memberships"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("client", "name")
        ordering = ["client__name", "name"]

    def __str__(self):
        return f"{self.client} • {self.name}"


# /**
#  * Task
#  * A task within a project, optionally assigned to a user.
#  * @property {int} id - Primary key.
#  * @property {Project} project - Parent project (FK).
#  * @property {string} title - Task title (max_length=160).
#  * @property {string|null} description - Optional description.
#  * @property {User|null} assignee - Optional assignee (nullable FK).
#  * @property {"todo"|"in_progress"|"done"} status - Task status.
#  * @property {decimal} estimate_hours - Estimated hours (Decimal, default=0).
#  * @property {date|null} due_date - Optional due date.
#  * @property {datetime} created_at - Creation timestamp (auto_now_add).
#  * @relation {TimeEntry[]} time_entries - Reverse FK from TimeEntry.
#  */
class Task(models.Model):
    STATUS = [("todo", "To Do"), ("in_progress", "In Progress"), ("done", "Done")]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True, null=True)
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    status = models.CharField(max_length=20, choices=STATUS, default="todo")
    estimate_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.title


# /**
#  * TimeEntry
#  * Logged time against a task by a user on a specific date.
#  * @property {int} id - Primary key.
#  * @property {Task} task - Related task (FK).
#  * @property {User} user - User who logged the time (FK).
#  * @property {date} date - The date of the work.
#  * @property {decimal} hours - Number of hours (Decimal).
#  * @property {string|null} note - Optional short note (max_length=255).
#  * @property {datetime} created_at - Creation timestamp (auto_now_add).
#  */
class TimeEntry(models.Model):
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="time_entries"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="time_entries"
    )
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    note = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
