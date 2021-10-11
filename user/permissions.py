from user import utils
from rest_framework import  permissions
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView


class IsRegular(BasePermission):
    message = 'Вам не разрешено выполнять эту операцию'

    def has_permission(self, request, view):
        user = request.user
        if user.is_anonymous:
            return False
        return bool(user.type == 1 or user.is_staff)


class IsStoreOrReadOnly(BasePermission):
    message = 'Вам не разрешено выполнять эту операцию'

    def has_permission(self, request, view):
        user = request.user

        if user.is_authenticated and request.method in permissions.SAFE_METHODS:
            return True

        return bool(user.type == 2 or user.is_staff)