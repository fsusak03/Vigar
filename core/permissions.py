from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                user.is_superuser
                or user.groups.filter(name__iexact="admin").exists()
            )
        )

class IsProjectMemberOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        project = getattr(obj, "project", obj)
        if hasattr(project, "project"):  # TimeEntry -> task.project
            project = project.project
        return request.user.is_authenticated and project.members.filter(pk=request.user.pk).exists()
