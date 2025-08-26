from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Client, Project
from core.services import add_project_member, create_task


class Command(BaseCommand):
    help = "Seed demo data (client, project, task) and link first user)"

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.first()
        if not user:
            self.stdout.write(
                self.style.WARNING("No users found. Create a superuser first.")
            )
            return

        client, _ = Client.objects.get_or_create(name="ACME")
        project, _ = Project.objects.get_or_create(client=client, name="Website")
        add_project_member(project, user)
        create_task(project=project, title="Initial setup", assignee=user)
        self.stdout.write(self.style.SUCCESS("Seeded demo data."))
