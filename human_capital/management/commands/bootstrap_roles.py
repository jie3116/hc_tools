from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from human_capital.access import ROLE_ADMIN_HC, ROLE_APPROVER, ROLE_EMPLOYEE


class Command(BaseCommand):
    help = "Create default groups for Human Capital roles."

    def handle(self, *args, **options):
        for role_name in (ROLE_EMPLOYEE, ROLE_ADMIN_HC, ROLE_APPROVER):
            Group.objects.get_or_create(name=role_name)
        self.stdout.write(self.style.SUCCESS("Default Human Capital roles are ready."))
