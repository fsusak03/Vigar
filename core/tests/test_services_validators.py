import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from core import services as svc
from core import validators as val
from core.models import Client, Project, Task

User = get_user_model()


class ServicesValidatorsTests(TestCase):
    def test_validate_member_is_in_project_happy(self):
        user = User.objects.create_user(username="u1", password="pass")
        client = Client.objects.create(name="C1")
        project = Project.objects.create(client=client, name="P1")
        project.members.add(user)

        # should not raise
        val.validate_member_is_in_project(user, project)

    def test_validate_member_is_in_project_raises_when_not_member(self):
        user = User.objects.create_user(username="u1", password="pass")
        client = Client.objects.create(name="C1")
        project = Project.objects.create(client=client, name="P1")

        with self.assertRaises(ValidationError):
            val.validate_member_is_in_project(user, project)

    def test_create_project_enforces_unique_name_per_client(self):
        client = Client.objects.create(name="C1")
        svc.create_project(client=client, name="Proj")
        with self.assertRaises(ValidationError):
            svc.create_project(client=client, name="Proj")

    def test_create_task_checks_assignee_membership(self):
        client = Client.objects.create(name="C1")
        project = svc.create_project(client=client, name="Proj")
        assignee = User.objects.create_user(username="u1", password="pass")

        # Not a member -> should raise
        with self.assertRaises(ValidationError):
            svc.create_task(project=project, title="T1", assignee=assignee)

        # Add member -> should pass
        svc.add_project_member(project, assignee)
        task = svc.create_task(project=project, title="T1", assignee=assignee)
        self.assertIsInstance(task, Task)

    def test_log_time_validations(self):
        user = User.objects.create_user(username="u1", password="pass")
        client = Client.objects.create(name="C1")
        project = svc.create_project(client=client, name="Proj")
        svc.add_project_member(project, user)
        task = svc.create_task(project=project, title="T1")

        # Future date -> invalid
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        with self.assertRaises(ValidationError):
            svc.log_time(task=task, user=user, date=tomorrow, hours=1)

        # Non-positive hours -> invalid
        today = datetime.date.today()
        with self.assertRaises(ValidationError):
            svc.log_time(task=task, user=user, date=today, hours=0)

        # Happy path
        entry = svc.log_time(task=task, user=user, date=today, hours=1.5)
        self.assertAlmostEqual(float(entry.hours), 1.5)
