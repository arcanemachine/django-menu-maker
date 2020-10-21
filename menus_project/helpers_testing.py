from restaurants.models import Restaurant
from menus.models import Menu, MenuSection
from django.contrib.auth import get_user_model

from restaurants.models import Restaurant

test_restaurant_name = 'Test Restaurant'
test_menu_name = 'Test Menu'

def create_test_user(username='test_user', password='password'):

    if not type(username) == str:
        raise TypeError('username must be a string')
    elif not type(password) == str:
        raise TypeError('password must be a string')

    user = get_user_model().objects.create(username=username)
    user.set_password(password)
    user.save()
    return user

def create_test_restaurant(name=test_restaurant_name, admin_users=[]):

    if not type(name) == str:
        raise TypeError('name must be a string')

    if not type(admin_users) == list:
        raise TypeError('admin_users must be a list')
    elif admin_users:
        for user in admin_users:
            if not type(user) == get_user_model():
                raise TypeError("admin_users must contain objects of type: "\
                        f"{get_user_model()}")

    restaurant = Restaurant.objects.create(name=name)
    restaurant.admin_users.set(admin_users)

    return restaurant

def create_test_menu(restaurant, name=test_menu_name, theme='default'):

    if not isinstance(restaurant, Restaurant):
        raise TypeError("restaurant must be a Restaurant object")

    if not type(name) == str:
        raise TypeError("name must be a string")

    theme_choices = [choice[0] for choice in restaurant.THEME_CHOICES]
    if not type(theme) == str:
        raise TypeError("theme must be string")
    elif not theme in theme_choices:
        raise ValueError("theme must be one of the following: "\
                f"{', '.join(theme_choices)}")

    menu = Menu.objects.create(
            restaurant=restaurant,
            name=name,
            theme=theme)
    return menu

def create_test_menu_section(menu, name="Test Menu Section")
    menu_section = MenuSection.objects.create(
            menu=menu,
            name=name)
    return menu_section
