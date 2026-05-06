from __future__ import annotations

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


ROLE_EMPLOYEE = "employee"
ROLE_ADMIN_HC = "admin_hc"
ROLE_APPROVER = "approver"


def user_has_role(user, *roles: str) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=roles).exists()


def get_user_roles(user) -> list[str]:
    if not user.is_authenticated:
        return []
    if user.is_superuser:
        return ["superuser"]
    return list(user.groups.order_by("name").values_list("name", flat=True))


def require_roles(*roles: str):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not user_has_role(request.user, *roles):
                raise PermissionDenied("You do not have access to this resource.")
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
