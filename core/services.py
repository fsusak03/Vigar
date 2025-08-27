from typing import Iterable, Optional

from django.db import transaction

from .models import Project, Task, TimeEntry
from .validators import (
    validate_member_is_in_project,
    validate_project_dates,
    validate_time_entry,
    validate_unique_project_name_within_client,
)


@transaction.atomic
# /**
#  * Add a user to a project's members.
#  * Transactional: yes.
#  * @param {Project} project - The project to modify.
#  * @param {User} user - The user to add as a member.
#  * @returns {Project} The updated project instance.
#  */
def add_project_member(project: Project, user):
    project.members.add(user)
    return project


@transaction.atomic
# /**
#  * Remove a user from a project's members.
#  * Also unassigns all tasks in that project assigned to the user.
#  * Transactional: yes.
#  * @param {Project} project - The project to modify.
#  * @param {User} user - The user to remove.
#  * @returns {Project} The updated project instance.
#  */
def remove_project_member(project: Project, user):
    project.members.remove(user)
    # Optionally unassign user's tasks in this project
    Task.objects.filter(project=project, assignee=user).update(assignee=None)
    return project


@transaction.atomic
# /**
#  * Create a new project with optional initial members.
#  * Validates uniqueness of name within client and date consistency.
#  * Transactional: yes.
#  * @param {Client} client - Owning client.
#  * @param {string} name - Project name.
#  * @param {string} [description] - Optional description.
#  * @param {date|null} [start_date]
#  * @param {date|null} [deadline]
#  * @param {"active"|"on_hold"|"completed"} [status]
#  * @param {Iterable<User>} [members]
#  * @returns {Project} The created project.
#  * @throws {ValidationError} If name not unique per client or dates invalid.
#  */
def create_project(
    *,
    client,
    name: str,
    description: str = "",
    start_date=None,
    deadline=None,
    status: str = "active",
    members: Optional[Iterable] = None,
) -> Project:
    validate_unique_project_name_within_client(client, name)
    validate_project_dates(start_date, deadline)
    project = Project.objects.create(
        client=client,
        name=name.strip(),
        description=description,
        start_date=start_date,
        deadline=deadline,
        status=status,
    )
    if members:
        project.members.add(*members)
    return project


@transaction.atomic
# /**
#  * Update mutable fields on a project with validation.
#  * If name provided, enforces uniqueness within the same client.
#  * If dates provided, validates start <= deadline.
#  * Transactional: yes.
#  * @param {Project} project - Project to update.
#  * @param {string} [name]
#  * @param {string} [description]
#  * @param {date|null} [start_date]
#  * @param {date|null} [deadline]
#  * @param {"active"|"on_hold"|"completed"} [status]
#  * @returns {Project} The updated project.
#  * @throws {ValidationError} On uniqueness or date validation errors.
#  */
def update_project(
    project: Project,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    start_date=None,
    deadline=None,
    status: Optional[str] = None,
) -> Project:
    if name is not None:
        validate_unique_project_name_within_client(
            project.client, name, exclude_project_id=project.id
        )
        project.name = name.strip()
    if description is not None:
        project.description = description
    if start_date is not None or deadline is not None:
        validate_project_dates(
            start_date or project.start_date, deadline or project.deadline
        )
        if start_date is not None:
            project.start_date = start_date
        if deadline is not None:
            project.deadline = deadline
    if status is not None:
        project.status = status
    project.save()
    return project


@transaction.atomic
# /**
#  * Create a new task within a project.
#  * Validates that assignee (if provided) is a project member.
#  * Transactional: yes.
#  * @param {Project} project - Parent project.
#  * @param {string} title - Task title.
#  * @param {User|null} [assignee] - Optional assignee.
#  * @param {any} kwargs - Additional model fields (description, status,
#  *   estimate_hours, due_date).
#  * @returns {Task} The created task.
#  * @throws {ValidationError} If assignee is not a member of the project.
#  */
def create_task(*, project: Project, title: str, assignee=None, **kwargs) -> Task:
    if assignee:
        validate_member_is_in_project(assignee, project)
    return Task.objects.create(
        project=project, title=title.strip(), assignee=assignee, **kwargs
    )


@transaction.atomic
# /**
#  * Reassign a task to a new assignee or clear the assignee.
#  * Validates that new assignee (if provided) is a project member.
#  * Transactional: yes.
#  * @param {Task} task - The task to update.
#  * @param {User|null} [assignee] - New assignee or None to unassign.
#  * @returns {Task} The updated task.
#  * @throws {ValidationError} If assignee is not a member of the project.
#  */
def reassign_task(task: Task, *, assignee=None) -> Task:
    if assignee:
        validate_member_is_in_project(assignee, task.project)
    task.assignee = assignee
    task.save(update_fields=["assignee"])
    return task


@transaction.atomic
# /**
#  * Log time for a task by a user on a date with given hours.
#  * Validates positive hours and non-future date.
#  * Permits logging if the user is the task assignee or a project member.
#  * Transactional: yes.
#  * @param {Task} task - The task to log time against.
#  * @param {User} user - The user who is logging time.
#  * @param {date} date - The date of work.
#  * @param {Decimal|float|int} hours - The number of hours.
#  * @param {string|null} [note] - Optional note.
#  * @returns {TimeEntry} The created time entry.
#  * @throws {ValidationError} If hours/date invalid.
#  * @throws {ValueError} If user is not permitted to log time on the task.
#  */
def log_time(*, task: Task, user, date, hours, note=None) -> TimeEntry:
    validate_time_entry(date, hours)
    # Ensure user is allowed: either assignee or project member
    user_id = getattr(user, "id", None)
    # Normalize to int for pk lookup to satisfy type checkers
    if not isinstance(user_id, int):
        user_id = -1
    if not (
        task.assignee_id == user_id or task.project.members.filter(pk=user_id).exists()
    ):
        raise ValueError("User is not permitted to log time for this task.")
    return TimeEntry.objects.create(
        task=task, user=user, date=date, hours=hours, note=note
    )
