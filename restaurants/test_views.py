from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from html import unescape

from .models import Restaurant
from menus_project import constants

test_user_username = constants.TEST_USER_USERNAME
test_user_password = constants.TEST_USER_PASSWORD
test_restaurant_name = constants.TEST_RESTAURANT_NAME
restaurant_admin_user_username = constants.RESTAURANT_ADMIN_USER_USERNAME
restaurant_admin_user_password = constants.RESTAURANT_ADMIN_USER_PASSWORD


class RestaurantListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # create test user
        cls.test_user = \
                get_user_model().objects.create(username=test_user_username)
        cls.test_user.set_password(test_user_password)
        cls.test_user.save()

        # create test restaurant
        cls.test_restaurant = \
            Restaurant.objects.create(name=test_restaurant_name)
        cls.test_restaurant.admin_users.set([cls.test_user])
        cls.test_restaurant.save()

        cls.current_test_url = reverse('restaurants:restaurant_list')

    def setUp(self):
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.view = self.context['view']

    def test_view_class_name(self):
        self.assertEqual(self.view.__class__.__name__, 'RestaurantListView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'ListView')

    def test_model(self):
        self.assertEqual(self.view.model.__name__, 'Restaurant')

    def test_context_object_name_is_restaurants(self):
        self.assertTrue('restaurants' in self.context)

    # request.GET
    def test_get_method_unauthenticated_user(self):
        self.assertEqual(self.response.status_code, 200)


class RestaurantCreateViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # create restaurant admin user
        cls.restaurant_admin_user = get_user_model().objects.create(
            username=restaurant_admin_user_username)
        cls.restaurant_admin_user.set_password(restaurant_admin_user_password)
        cls.restaurant_admin_user.save()

        cls.current_test_url = reverse('restaurants:restaurant_create')

    def setUp(self):
        self.client.login(
            username=self.restaurant_admin_user.username,
            password=restaurant_admin_user_password)

        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))
        self.view = self.response.context['view']

    # view attributes
    def test_view_class_name(self):
        self.assertEqual(self.view.__class__.__name__, 'RestaurantCreateView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'CreateView')

    def test_which_mixins_are_used(self):
        self.assertEqual(
            self.view.__class__.__bases__[0].__name__, 'LoginRequiredMixin')

    def test_model_name(self):
        self.assertEqual(self.view.model.__name__, 'Restaurant')

    def test_fields(self):
        self.assertEqual(self.view.fields, ('name',))

    def test_success_message(self):
        self.assertEqual(
            self.view.success_message, "Restaurant Created: %(name)s")

    # get_context_data()
    def test_context_has_action_verb(self):
        self.assertTrue('action_verb' in self.context)

    def test_context_has_correct_action_verb(self):
        self.assertEqual(self.context['action_verb'], 'Create')

    # request.GET
    def test_get_method(self):
        self.assertEqual(self.response.status_code, 200)

    # template
    def test_template_contains_proper_form_text(self):
        self.assertIn(
            "Please enter the information for your restaurant:", self.html)

    # request.POST
    def test_post_method_authorized_user(self):
        # get restaurant count before POST
        old_restaurant_count = Restaurant.objects.count()

        # create new restaurant via POST
        self.response = self.client.post(
            self.current_test_url, {'name': test_restaurant_name})
        self.html = unescape(self.response.content.decode('utf-8'))

        # user is redirected to restaurant_detail
        new_restaurant = Restaurant.objects.get(name=test_restaurant_name)
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, new_restaurant.get_absolute_url())

        # page loads successfully and uses proper template and expected text
        self.response = self.client.get(self.response.url)
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertEqual(self.response.status_code, 200)
        self.assertIn(f"{new_restaurant.name}", self.html)
        self.assertIn("Add New Menu", self.html)

        # template contains success_message
        self.assertIn(
            f"Restaurant Created: {new_restaurant.name}", self.html)

        # restaurant count increased by 1
        new_restaurant_count = Restaurant.objects.count()
        self.assertEqual(old_restaurant_count + 1, new_restaurant_count)

    # validation
    def test_validation_post_attempt_duplicate_by_authorized_user(self):
        Restaurant.objects.create(name=test_restaurant_name)

        # get restaurant count before attempting POST
        old_restaurant_count = Restaurant.objects.count()

        # attempt to create duplicate restaurant via POST
        self.response = self.client.post(
            self.current_test_url, {'name': test_restaurant_name})
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn("This name is too similar", self.html)

        # restaurant count should be unchanged
        new_restaurant_count = Restaurant.objects.count()
        self.assertEqual(old_restaurant_count, new_restaurant_count)

    def test_validation_post_attempt_by_user_with_too_many_restaurants(self):
        self.test_restaurants = []
        for i in range(constants.MAX_RESTAURANTS_PER_USER):
            self.test_restaurants.append(
                Restaurant.objects.create(
                    name=test_restaurant_name + f" {i+1}"))
            self.test_restaurants[i].admin_users.add(
                self.restaurant_admin_user)

        self.setUp()

        # template contains MAX_RESTAURANTS_PER_USER_ERROR_STRING
        self.assertIn(
            constants.MAX_RESTAURANTS_PER_USER_ERROR_STRING, self.html)

        # get restaurant count before attempting POST
        old_restaurant_count = Restaurant.objects.count()

        # attempt to create restaurant via POST
        self.response = self.client.post(
            self.current_test_url, {'name': test_restaurant_name})
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(
            constants.MAX_RESTAURANTS_PER_USER_ERROR_STRING, self.html)

        # restaurant count should be unchanged
        new_restaurant_count = Restaurant.objects.count()
        self.assertEqual(old_restaurant_count, new_restaurant_count)


class RestaurantDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # create test user
        cls.test_user = get_user_model().objects.create(
                username=test_user_username)
        cls.test_user.set_password(test_user_password)
        cls.test_user.save()

        # create test restaurant
        cls.test_restaurant = Restaurant.objects.create(
            name=test_restaurant_name)
        cls.test_restaurant.admin_users.set([cls.test_user])
        cls.test_restaurant.save()

        cls.current_test_url = reverse(
            'restaurants:restaurant_detail', kwargs={
                'restaurant_slug': cls.test_restaurant.slug})

    def setUp(self):
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))
        self.view = self.context['view']

    # view attributes
    def test_view_class_name(self):
        self.assertEqual(self.view.__class__.__name__, 'RestaurantDetailView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, "DetailView")

    def test_model_name(self):
        self.assertEqual(self.view.model.__name__, 'Restaurant')

    # request.GET
    def test_get_method_unauthenticated_user(self):
        self.assertEqual(self.response.status_code, 200)

    # template
    def test_template_unauthorized_user_cannot_view_auth_links(self):
        self.assertNotIn('Add New Menu', self.html)

    def test_template_authorized_user_can_view_auth_links(self):
        self.client.login(
            username=self.test_user.username,
            password=test_user_password)
        self.setUp()
        self.assertIn('Add New Menu', self.html)

    # bad kwargs
    def test_bad_kwargs(self):
        self.response = self.client.get(
            reverse('restaurants:restaurant_detail', kwargs={
                'restaurant_slug': 'bad-slug'}))
        self.assertEqual(self.response.status_code, 404)
