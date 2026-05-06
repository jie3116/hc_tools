from __future__ import annotations

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from human_capital.access import ROLE_ADMIN_HC, ROLE_APPROVER, ROLE_EMPLOYEE
from human_capital.models import Employee

User = get_user_model()


class Command(BaseCommand):
    help = "Create demo users, assign roles, and link the employee account to an Employee profile."

    def handle(self, *args, **options):
        for role_name in (ROLE_EMPLOYEE, ROLE_ADMIN_HC, ROLE_APPROVER):
            Group.objects.get_or_create(name=role_name)

        accounts = [
            {
                "username": "hc-admin",
                "password": "hc-admin-123",
                "email": "hc-admin@example.com",
                "group": ROLE_ADMIN_HC,
                "is_staff": True,
                "employee_code": None,
            },
            {
                "username": "hc-approver",
                "password": "hc-approver-123",
                "email": "hc-approver@example.com",
                "group": ROLE_APPROVER,
                "is_staff": True,
                "employee_code": None,
            },
            {
                "username": "hc-employee",
                "password": "hc-employee-123",
                "email": "budi@company.com",
                "group": ROLE_EMPLOYEE,
                "is_staff": False,
                "employee_code": "EMP-001",
            },
        ]

        for account in accounts:
            user, created = User.objects.get_or_create(
                username=account["username"],
                defaults={
                    "email": account["email"],
                    "is_staff": account["is_staff"],
                },
            )
            if created:
                user.set_password(account["password"])
                user.save(update_fields=["password"])
            else:
                updated = False
                if user.email != account["email"]:
                    user.email = account["email"]
                    updated = True
                if user.is_staff != account["is_staff"]:
                    user.is_staff = account["is_staff"]
                    updated = True
                if updated:
                    user.save(update_fields=["email", "is_staff"])

            user.groups.add(Group.objects.get(name=account["group"]))

            employee_code = account["employee_code"]
            if employee_code:
                employee = Employee.objects.filter(employee_code=employee_code).first()
                if employee:
                    if employee.user_id != user.id:
                        employee.user = user
                        employee.save(update_fields=["user"])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Linked employee {employee.employee_code} to user {user.username}."
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Employee {employee_code} not found. User {user.username} created without profile link."
                        )
                    )

            action = "Created" if created else "Updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"{action} user {user.username} with role {account['group']}."
                )
            )
