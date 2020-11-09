from rest_framework import permissions

from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem


class HasRestaurantPermissionsOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS \
                and request.user.is_authenticated:
            return True
        elif request.user.is_staff:
            return True
        elif type(obj) == Restaurant:
            return request.user in obj.admin_users.all()
        elif type(obj) == Menu:
            return request.user in obj.restaurant.admin_users.all()
        elif type(obj) == MenuSection:
            return request.user in obj.menu.restaurant.admin_users.all()
        elif type(obj) == Menu:
            return request.user \
                in obj.menusection.menu.restaurant.admin_users.all()
        else:
            return False
