from rest_framework.permissions import BasePermission


class IsDonoCaderno(BasePermission):
    message = "Você não possui permissão para acessar este caderno."

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "aluno_id", None) == request.user.pk


class IsDonoPagina(BasePermission):
    message = "Você não possui permissão para acessar esta página."

    def has_object_permission(self, request, view, obj):
        return (
            obj.caderno.aluno_id == request.user.pk
            and obj.caderno.data_exclusao is None
            and obj.data_exclusao is None
        )
