from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission

from human_capital.access import ROLE_ADMIN_HC, ROLE_APPROVER, ROLE_EMPLOYEE, user_has_role


class EmployeeApiPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return user_has_role(request.user, ROLE_ADMIN_HC, ROLE_APPROVER)
        return user_has_role(request.user, ROLE_ADMIN_HC)


class PolicyDocumentApiPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return user_has_role(request.user, ROLE_ADMIN_HC, ROLE_APPROVER, ROLE_EMPLOYEE)
        return user_has_role(request.user, ROLE_ADMIN_HC)


class LetterTemplateApiPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return user_has_role(request.user, ROLE_ADMIN_HC, ROLE_APPROVER)
        return user_has_role(request.user, ROLE_ADMIN_HC)


class LetterRequestApiPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return user_has_role(request.user, ROLE_ADMIN_HC, ROLE_APPROVER, ROLE_EMPLOYEE)
        return user_has_role(request.user, ROLE_ADMIN_HC, ROLE_EMPLOYEE)


class PolicyChatApiPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and user_has_role(request.user, ROLE_ADMIN_HC, ROLE_APPROVER, ROLE_EMPLOYEE)
        )
