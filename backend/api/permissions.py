from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorOrReadOnly(BasePermission):
    message = 'Изменение чужого контента запрещено!'

    def has_object_permission(self, request, view, obj) -> bool:
        return request.method in SAFE_METHODS or request.user == obj.author


class AdminOrReadOnly(BasePermission):
    message = 'Действие доступно только администратору.'

    def has_permission(self, request, view) -> bool:
        if request.user.is_authenticated:
            return request.method in SAFE_METHODS or request.user.is_admin
        return request.method in SAFE_METHODS
