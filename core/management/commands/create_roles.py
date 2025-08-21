from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Create default roles (groups): admin, manager, member"

    def handle(self, *args, **options):
        for name in ["admin", "manager", "member"]:
            Group.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Roles ensured: admin, manager, member"))
