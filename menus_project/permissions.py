from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem


class UserHasRestaurantPermissionsMixin(UserPassesTestMixin):

    def test_func(self, obj=None):

        # if the view is a CreateView, get object from self.[obj]
        if not obj and 'CreateView' in \
                [klass.__name__ for klass in self.__class__.__bases__]:

            if hasattr(self, 'restaurant'):
                obj = self.restaurant
            elif hasattr(self, 'menu'):
                obj = self.menu
            elif hasattr(self, 'menusection'):
                obj = self.menusection
            elif hasattr(self, 'menuitem'):
                obj = self.menuitem
        
        # if the view is not a CreateView, get object from self.get_object()
        if not obj:
            obj = self.get_object()
        
        if type(obj) == Restaurant:
            if self.request.user in obj.admin_users.all() \
                    or self.request.user.is_staff:
                return True
            else:
                return False
        elif type(obj) == Menu:
            if self.request.user in obj.restaurant.admin_users.all() \
                    or self.request.user.is_staff:
                return True
            else:
                return False
        elif type(obj) == MenuSection:
            if self.request.user in obj.menu.restaurant.admin_users.all() \
                    or self.request.user.is_staff:
                return True
            else:
                return False
        elif type(obj) == MenuItem:
            if self.request.user in \
                    obj.menusection.menu.restaurant.admin_users.all() \
                    or self.request.user.is_staff:
                return True
            else:
                return False
        return False
