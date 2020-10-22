from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Menu
from restaurants.models import Restaurant

class MenuDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        # create unprivileged user
        cls.test_user = get_user_model().objects.create(username='test_user')
        cls.test_user.set_password('password')
        cls.test_user.save()

        # create restaurant admin user
        cls.restaurant_admin_user = \
            get_user_model().objects.create(username='restaurant_admin_user')
        cls.restaurant_admin_user.set_password('password')
        cls.restaurant_admin_user.save()

        # create test restaurant
        cls.test_restaurant = \
            Restaurant.objects.create(name='Test Restaurant')
        cls.test_restaurant.admin_users.add(cls.restaurant_admin_user)

        # create test menu
        cls.test_menu = Menu.objects.create(
                restaurant=cls.test_restaurant,
                name='Test Menu')

    def setUp(self):
        self.response = self.client.get(
            reverse('menus:menu_detail', kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': self.test_menu.slug,
                }))
        self.context = self.response.context
        self.html = self.response.content.decode('utf-8')


