from django.contrib.auth import get_user_model

import factory

from menus_project import constants as c
from restaurants.models import Restaurant
from menus.models import Menu, MenuSection, MenuItem

"""
Usage:
    - Create object and save: e.g. user = UserFactory()
    - Build object but don't save: e.g. user = UserFactory.build()
"""


# user
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f'{c.TEST_USER_USERNAME}_{n+1}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@email.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.PostGenerationMethodCall(
        'set_password', c.TEST_USER_PASSWORD)
    is_staff = False


# restaurant
class RestaurantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Restaurant

    name = factory.Sequence(lambda n: f'{c.TEST_RESTAURANT_NAME} {n+1}')

    @factory.post_generation
    def admin_users(self, create, extracted, **kwargs):
        """
        Add user to admin_users:
            - RestaurantFactory(admin_users=[user])
        """
        # if object not saved to database, do nothing
        if not create:
            return

        # if object saved to database, add users to admin_users
        if extracted:
            for user in extracted:
                self.admin_users.add(user)


class RandomRestaurantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Restaurant

    name = factory.Faker('company')


# menu
class MenuFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Menu

    restaurant = factory.SubFactory(RestaurantFactory)
    name = factory.Sequence(lambda n: f'{c.TEST_MENU_NAME} {n+1}')

    @factory.post_generation
    def admin_users(self, create, extracted, **kwargs):
        """
        Add user to restaurant.admin_users:
            - MenuFactory(admin_users=[user])
        """
        # if object not saved to database, do nothing
        if not create:
            return

        # if object saved to database, add users to admin_users
        if extracted:
            for user in extracted:
                self.restaurant.admin_users.add(user)


# menu section
class MenuSectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MenuSection

    menu = factory.SubFactory(MenuFactory)
    name = factory.Sequence(lambda n: f'{c.TEST_MENUSECTION_NAME} {n+1}')

    @factory.post_generation
    def admin_users(self, create, extracted, **kwargs):
        """
        Add user to menu.restaurant.admin_users:
            - MenuSectionFactory(admin_users=[user])
        """
        # if object not saved to database, do nothing
        if not create:
            return

        # if object saved to database, add users to admin_users
        if extracted:
            for user in extracted:
                self.menu.restaurant.admin_users.add(user)


# menu item
class MenuItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MenuItem

    menusection = factory.SubFactory(MenuSectionFactory)
    name = factory.Sequence(lambda n: f'{c.TEST_MENUITEM_NAME} {n+1}')
    description = \
        factory.Sequence(lambda n: f'{c.TEST_MENUITEM_DESCRIPTION} {n+1}')

    @factory.post_generation
    def admin_users(self, create, extracted, **kwargs):
        """
        Add user to menu.restaurant.admin_users:
            - MenuSectionFactory(admin_users=[user])
        """
        # if object not saved to database, do nothing
        if not create:
            return

        # if object saved to database, add users to admin_users
        if extracted:
            for user in extracted:
                self.menusection.menu.restaurant.admin_users.add(user)
