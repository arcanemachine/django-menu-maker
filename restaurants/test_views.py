from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from html import unescape
from urllib.parse import urlparse

import factories as f
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
        cls.restaurant_admin_user = f.UserFactory()
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
        self.assertIn("auth-links", self.html)

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
        cls.restaurant_admin_user = f.UserFactory()
        cls.test_restaurant = \
            f.RestaurantFactory(admin_users=[cls.restaurant_admin_user])

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
        self.assertNotIn('auth-links', self.html)

    def test_template_authorized_user_can_view_auth_links(self):
        self.client.login(
            username=self.restaurant_admin_user.username,
            password=test_user_password)
        self.setUp()
        self.assertIn('auth-links', self.html)

    # bad kwargs
    def test_bad_kwargs(self):
        self.response = self.client.get(
            reverse('restaurants:restaurant_detail', kwargs={
                'restaurant_slug': 'bad-slug'}))
        self.assertEqual(self.response.status_code, 404)


class RestaurantUpdateViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user = f.UserFactory()
        cls.restaurant_admin_user = f.UserFactory()

    def setUp(self):
        self.test_restaurant = \
            f.RestaurantFactory(admin_users=[self.restaurant_admin_user])

        # login as authorized user
        self.client.login(
            username=self.restaurant_admin_user.username,
            password=restaurant_admin_user_password)

        self.current_test_url = reverse(
            'restaurants:restaurant_update', kwargs={
                'restaurant_slug': self.test_restaurant.slug})

        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))
        self.view = self.response.context['view']

    # view attributes
    def test_view_class_name(self):
        self.assertEqual(self.view.__class__.__name__, 'RestaurantUpdateView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'UpdateView')

    def test_which_mixins_are_used(self):
        self.assertEqual(
            self.view.__class__.__bases__[0].__name__, 'UserPassesTestMixin')
        self.assertEqual(
            self.view.__class__.__bases__[1].__name__, 'SuccessMessageMixin')

    def test_model_name(self):
        self.assertEqual(self.view.model.__name__, 'Restaurant')

    def test_fields(self):
        self.assertEqual(self.view.fields, ('name',))

    def test_success_message(self):
        self.assertEqual(
            self.view.success_message,
            "Restaurant Successfully Updated: %(name)s")

    # get_context_data()
    def test_context_has_action_verb(self):
        self.assertTrue('action_verb' in self.context)

    def test_context_has_correct_action_verb(self):
        self.assertEqual(self.context['action_verb'], 'Update')

    # get_initial()
    def test_method_get_initial(self):
        self.assertEqual(
            self.view.get_initial(), {'name': self.test_restaurant.name})

    # get_object()
    def test_method_get_object(self):
        self.assertEqual(self.view.get_object(), self.test_restaurant)

    # request.GET
    def test_get_method_unauthenticated_user(self):
        self.client.logout()

        # request by unauthenticated user should redirect to login
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 302)
        redirect_url = urlparse(self.response.url)[2]
        self.assertEqual(redirect_url, reverse('login'))

    def test_get_method_authenticated_but_unauthorized_user(self):
        self.client.login(
            username=self.test_user.username, password=test_user_password)

        # request by unauthorized user should return 403
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 403)

    def test_get_method_authorized_user(self):
        self.assertEqual(self.response.status_code, 200)

    def test_get_method_staff_user(self):
        # give staff privileges to self.test_user
        self.test_user.is_staff = True
        self.test_user.save()

        # reload the page
        self.response = self.client.get(self.current_test_url)

        # remove staff privileges from self.test_user
        self.test_user.is_staff = False
        self.test_user.save()

        self.assertEqual(self.response.status_code, 200)

    # template
    def test_template_contains_proper_intro_text(self):
        self.assertIn(
            "Please enter the information for your restaurant:", self.html)

    def test_template_form_contains_proper_initial_data_name(self):
        self.assertIn(rf'value="{self.test_restaurant.name}"', self.html)

    # request.POST
    def test_post_method_unauthenticated_user(self):
        self.client.logout()

        old_restaurant_name = self.test_restaurant.name
        updated_restaurant_name = f'Updated {self.test_restaurant.name}'

        # attempt to update self.test_restaurant via POST
        self.response = self.client.post(
            self.current_test_url, {'name': updated_restaurant_name})

        # user is redirected to login page
        self.assertEqual(self.response.status_code, 302)
        redirect_url = urlparse(self.response.url)[2]
        self.assertEqual(redirect_url, reverse('login'))

        # self.test_restaurant is unchanged
        self.test_restaurant.refresh_from_db()
        self.assertEqual(self.test_restaurant.name, old_restaurant_name)

    def test_post_method_authenticated_but_unauthorized_user(self):
        self.client.login(
            username=self.test_user.username, password=test_user_password)

        old_restaurant_name = self.test_restaurant.name
        updated_restaurant_name = f'Updated {self.test_restaurant.name}'

        # attempt to update self.test_restaurant via POST
        self.response = self.client.post(self.current_test_url, {
            'name': updated_restaurant_name})

        # user receives HTTP 403
        self.assertEqual(self.response.status_code, 403)

        # self.test_restaurant is unchanged
        self.test_restaurant.refresh_from_db()
        self.assertEqual(self.test_restaurant.name, old_restaurant_name)

    def test_post_method_authorized_user(self):
        updated_restaurant_name = f'Updated {self.test_restaurant.name}'
        updated_restaurant_slug = slugify(updated_restaurant_name)

        # get restaurant count before POST
        old_restaurant_count = Restaurant.objects.count()

        # update self.test_restaurant via POST
        self.response = self.client.post(
            self.current_test_url, {'name': updated_restaurant_name})
        self.html = unescape(self.response.content.decode('utf-8'))

        # self.test_restaurant has been updated with new values
        self.test_restaurant.refresh_from_db()
        self.assertEqual(self.test_restaurant.name, updated_restaurant_name)
        self.assertEqual(self.test_restaurant.slug, updated_restaurant_slug)

        # user is redirected to restaurant_detail
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, self.test_restaurant.get_absolute_url())

        # restaurant_detail loads successfully and uses proper template
        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(
            self.response, 'restaurants/restaurant_detail.html')

        # template contains new restaurant values
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(f"{self.test_restaurant.name}", self.html)

        # template contains success_message
        self.assertIn(
            f"Restaurant Successfully Updated: {updated_restaurant_name}",
            self.html)

        # restaurant count has not changed
        updated_restaurant_count = Restaurant.objects.count()
        self.assertEqual(old_restaurant_count, updated_restaurant_count)

    # validation
    def test_validation_post_attempt_duplicate_by_authorized_user(self):
        self.test_restaurant_2 = \
            Restaurant.objects.create(name='{self.test_restaurant} 2')
        self.test_restaurant_2.admin_users.add(self.restaurant_admin_user)

        old_restaurant_name = self.test_restaurant.name
        old_restaurant_slug = self.test_restaurant.slug

        updated_restaurant_name = self.test_restaurant_2.name

        # attempt to update self.test_restaurant via POST
        self.response = self.client.post(
            self.current_test_url, {'name': updated_restaurant_name})
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn("This name is too similar", self.html)

        # self.test_restaurant still has original values
        self.test_restaurant.refresh_from_db()
        self.assertEqual(self.test_restaurant.name, old_restaurant_name)
        self.assertEqual(self.test_restaurant.slug, old_restaurant_slug)

    # bad kwargs
    def test_bad_kwargs(self):
        for i in range(len(self.view.kwargs)):
            self.current_test_url = \
                reverse('restaurants:restaurant_update', kwargs={
                    'restaurant_slug':
                        self.test_restaurant.slug if i != 0 else 'bad-slug'})
            self.response = self.client.get(self.current_test_url)
            self.assertEqual(self.response.status_code, 404)


class RestaurantDeleteViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user = f.UserFactory()
        cls.restaurant_admin_user = f.UserFactory()
        cls.test_restaurant = \
            f.RestaurantFactory(admin_users=[cls.restaurant_admin_user])

        cls.current_test_url = reverse(
            'restaurants:restaurant_delete', kwargs={
                'restaurant_slug': cls.test_restaurant.slug})

    def setUp(self):
        # login as authorized user
        self.client.login(
            username=self.restaurant_admin_user.username,
            password=restaurant_admin_user_password)

        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = unescape(self.response.content.decode('utf-8'))
        self.view = self.response.context['view']

    # view attributes
    def test_view_class_name(self):
        self.assertEqual(
            self.view.__class__.__name__, 'RestaurantDeleteView')

    def test_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'DeleteView')

    def test_which_mixins_are_used(self):
        self.assertEqual(
            self.view.__class__.__bases__[0].__name__, 'UserPassesTestMixin')

    def test_attribute_model_name(self):
        self.assertEqual(
            self.view.model.__name__, 'Restaurant')

    def test_attribute_success_message(self):
        self.assertEqual(
            self.view.success_message,
            "The '%(name)s' restaurant has been deleted.")

    def test_attribute_success_url(self):
        self.assertEqual(
            self.view.success_url, reverse('users:user_detail'))

    # delete()
    def test_method_delete_contains_proper_success_message(self):
        self.assertEqual(
            self.view.success_message % self.test_restaurant.__dict__,
            f"The '{self.test_restaurant.name}' restaurant has been deleted.")

    # get_object()
    def test_method_get_object(self):
        self.assertEqual(self.view.get_object(), self.test_restaurant)

    # request.GET
    def test_get_method_unauthenticated_user(self):
        self.client.logout()

        # request by unauthenticated user should redirect to login
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 302)
        redirect_url = urlparse(self.response.url)[2]
        self.assertEqual(redirect_url, reverse('login'))

    def test_get_method_authenticated_but_unauthorized_user(self):
        self.client.login(
            username=self.test_user.username, password=test_user_password)

        # request by unauthorized user should return 403
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 403)

    def test_get_method_authorized_user(self):
        self.assertEqual(self.response.status_code, 200)

    def test_get_method_staff_user(self):
        # give staff privileges to self.test_user
        self.test_user.is_staff = True
        self.test_user.save()

        # reload the page
        self.response = self.client.get(self.current_test_url)

        # remove staff privileges from self.test_user
        self.test_user.is_staff = False
        self.test_user.save()

        self.assertEqual(self.response.status_code, 200)

    # template
    def test_template_contains_proper_confirm_text(self):
        self.assertIn(
            fr"Are you sure you want to delete the "
            fr"'{self.test_restaurant.name}' restaurant?", self.html)

    # request.POST
    def test_post_method_unauthenticated_user(self):
        self.client.logout()

        # get restaurant count before POST
        old_restaurant_count = Restaurant.objects.count()

        # attempt to delete self.test_restaurant
        self.response = self.client.post(self.current_test_url)

        # user is redirected to login page
        self.assertEqual(self.response.status_code, 302)
        redirect_url = urlparse(self.response.url)[2]
        self.assertEqual(redirect_url, reverse('login'))

        # restaurant count has not changed
        new_restaurant_count = Restaurant.objects.count()
        self.assertEqual(old_restaurant_count, new_restaurant_count)

    def test_post_method_authenticated_but_unauthorized_user(self):
        self.client.login(
            username=self.test_user.username, password=test_user_password)

        # get restaurant count before attempting POST
        old_restaurant_count = Restaurant.objects.count()

        # attempt to delete self.test_restaurant via POST
        self.response = self.client.post(self.current_test_url)

        # user receives HTTP 403
        self.assertEqual(self.response.status_code, 403)

        # restaurant count has not changed
        new_restaurant_count = Restaurant.objects.count()
        self.assertEqual(old_restaurant_count, new_restaurant_count)

    def test_post_method_authorized_user(self):
        # get restaurant count before attempting POST
        old_restaurant_count = Restaurant.objects.count()

        # restaurant_detail contains test_restaurant.name before delete
        self.response = self.client.get(
            self.test_restaurant.get_absolute_url())
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertIn(f"{self.test_restaurant.name}", self.html)

        # delete self.test_restaurant via POST
        self.response = self.client.post(self.current_test_url)

        # user is redirected to users:user_detail
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(
            self.response.url, reverse('users:user_detail'))

        # user_detail loads successfully and contains success_message
        self.response = self.client.get(self.response.url)
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(
            self.response, 'users/user_detail.html')
        self.assertIn(
            rf"The '{self.test_restaurant.name}' restaurant has been deleted.",
            self.html)

        # user_detail does not contain restaurant name after refresh
        self.response = self.client.get(reverse('users:user_detail'))
        self.html = unescape(self.response.content.decode('utf-8'))
        self.assertNotIn(f"{self.test_restaurant.name}", self.html)

        # object no longer exists
        with self.assertRaises(Restaurant.DoesNotExist):
            self.test_restaurant.refresh_from_db()

        # restaurant count decreased by 1
        new_restaurant_count = Restaurant.objects.count()
        self.assertEqual(old_restaurant_count - 1, new_restaurant_count)

    # validation
    def test_validation_post_attempt_duplicate_by_authorized_user(self):
        # delete self.test_restaurant
        self.test_restaurant.delete()

        # attempt POST request to delete already-deleted restaurant
        self.response = self.client.post(self.current_test_url)

        # returns HTTP 404
        self.assertEqual(self.response.status_code, 404)

    # bad kwargs
    def test_bad_kwargs(self):
        for i in range(len(self.view.kwargs)):
            self.current_test_url = \
                reverse('restaurants:restaurant_delete', kwargs={
                    'restaurant_slug':
                        self.test_restaurant.slug if i != 0 else 'bad-slug'})
            self.response = self.client.get(self.current_test_url)
            self.assertEqual(self.response.status_code, 404)
