from datetime import date

from django.core.exceptions import ValidationError


# /**
#  * Ensure a given user is a member of the specified project.
#  * @param {User|null} user - Assignee to validate (can be null/None).
#  * @param {Project} project - Project to check membership against.
#  * @throws {ValidationError} If user is provided and is not a project member.
#  */
def validate_member_is_in_project(user, project):
    if user and not project.members.filter(pk=user.pk).exists():
        raise ValidationError("Assignee must be a member of the project.")


# /**
#  * Enforce unique project name within a single client (case-insensitive).
#  * @param {Client} client - Owning client.
#  * @param {string} name - Proposed project name.
#  * @param {int|null} [exclude_project_id] - Existing project id to exclude
#  *   (for updates).
#  * @throws {ValidationError} If another project with the same name exists
#  *   for the client.
#  */
def validate_unique_project_name_within_client(
    client, name, *, exclude_project_id=None
):
    from .models import Project

    qs = Project.objects.filter(client=client, name__iexact=name.strip())
    if exclude_project_id:
        qs = qs.exclude(pk=exclude_project_id)
    if qs.exists():
        raise ValidationError("Project with this name already exists for this client.")


# /**
#  * Validate project date consistency (start_date must be <= deadline).
#  * @param {date|null} start_date
#  * @param {date|null} deadline
#  * @throws {ValidationError} If start_date is after deadline.
#  */
def validate_project_dates(start_date, deadline):
    if start_date and deadline and start_date > deadline:
        raise ValidationError("Project deadline cannot be before start date.")


# /**
#  * Validate time entry attributes (positive hours and non-future date).
#  * @param {date} date_value - Date of work.
#  * @param {Decimal|float|int} hours - Hours to log.
#  * @throws {ValidationError} If hours <= 0 or date is in the future.
#  */
def validate_time_entry(date_value: date, hours):
    if hours is None or hours <= 0:
        raise ValidationError("Hours must be a positive number.")
    # Optional: prevent future dates
    if date_value and date_value > date.today():
        raise ValidationError("Date cannot be in the future.")
