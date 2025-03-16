from rest_framework import permissions

class IsOperator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role.name == 'operator' if hasattr(request.user, 'role') else False 