from human_capital.access import get_user_roles


def user_roles(request):
    return {"user_roles": get_user_roles(request.user)}
