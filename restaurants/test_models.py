from django.contrib.auth import get_user_model
from django.test import TestCase

from menus_project import helpers_testing as ht

class RestaurantModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        user = ht.create_test_user()
        restaurant = ht.create_test_restaurant(admin_users=[user])

    def setUp(self):
        self.test_user = get_user_model().objects.first()

    ### FIELDS ###


    ### VALIDATION ###

    # do not allow duplicate restaurant slugs
    # require at least one admin user

    ### METHODS ###
