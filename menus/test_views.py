from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from inspect import getfullargspec
from urllib.parse import urlparse

from . import views
from .models import Menu, MenuSection
from restaurants.models import Restaurant

class MenusRootViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_restaurant = \
            Restaurant.objects.create(name='Test Restaurant')

    def setUp(self):
        self.view = views.menus_root
        self.current_test_url = reverse('menus:menus_root', kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                })
        self.response = self.client.get(self.current_test_url)

    # view attributes
    def test_view_name(self):
        self.assertEqual(self.view.__name__, 'menus_root')

    def test_view_get_arguments(self):
        view_args = getfullargspec(self.view)[0]
        return self.assertEqual(view_args, ['request', 'restaurant_slug'])

    # request.GET
    def test_view_get_method_unauthenticated_user(self):

        # response returns 302 redirect
        self.assertEqual(self.response.status_code, 302)

        # following the redirect will lead to restaurants:restaurant_detail
        self.response = self.client.get(self.current_test_url, follow=True)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.redirect_chain[0][0],
            reverse('restaurants:restaurant_detail', kwargs = {
                'restaurant_slug': self.test_restaurant.slug
                }))

    # bad kwargs
    def test_view_get_method_with_bad_kwargs_restaurant_slug(self):
        self.current_test_url = reverse('menus:menus_root', kwargs = {
                'restaurant_slug': 'bad-restaurant-slug',
                })

        # response returns 302 redirect
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 302)

        # following the redirect leads to 404 error
        self.response = self.client.get(self.current_test_url, follow=True)
        self.assertEqual(self.response.status_code, 404)

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
        cls.test_menu = cls.test_restaurant.menu_set.create(name='Test Menu')

    def setUp(self):
        self.current_test_url = reverse('menus:menu_detail', kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': self.test_menu.slug,
                })
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = self.response.content.decode('utf-8')
        self.view = self.response.context['view']

    # view attributes
    def test_view_name(self):
        self.assertEqual(self.view.__class__.__name__, 'MenuDetailView')

    def test_view_parent_class_name(self):
        self.assertEqual(
            self.context['view'].__class__.__bases__[0].__name__, 'DetailView')

    def test_view_model(self):
        self.assertEqual(self.context['view'].model.__name__, 'Menu')

    def test_slug_url_kwarg(self):
        self.assertEqual(self.context['view'].slug_url_kwarg, 'menu_slug')

    # bad kwargs
    def test_view_bad_kwargs_restaurant_slug(self):
        self.current_test_url = reverse('menus:menu_detail', kwargs = {
                'restaurant_slug': 'bad-slug',
                'menu_slug': self.test_menu.slug,
                })
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 404)

    def test_view_bad_kwargs_menu_slug(self):
        self.current_test_url = reverse('menus:menu_detail', kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': 'fake-slug',
                })
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 404)

    # request.GET
    def test_view_get_method_unauthenticated_user(self):
        self.assertEqual(self.response.status_code, 200)

    def test_unauthenticated_user_cannot_view_link_to_add_section(self):
        self.assertNotIn('Add New Section', self.html)

    # template - authentication-based conditions
    def test_unprivileged_user_cannot_view_link_to_add_section(self):
        self.client.login(
                username='test_user', password='password')

        self.setUp() # reload the page
        self.assertNotIn('Add New Section', self.html)

    def test_restaurant_admin_user_can_view_link_to_add_section(self):
        self.client.login(
                username='restaurant_admin_user', password='password')

        self.setUp() # reload the page
        self.assertIn('Add New Section', self.html)

    # template - number of menusections
    def test_menu_with_no_menusections(self):
        self.assertIn("This menu does not have any sections.", self.html)
        self.assertEqual(MenuSection.objects.count(), 0)

    def test_menu_with_1_menusection(self):
        test_menusection = \
                self.test_menu.menusection_set.create(name='Test Menu Section')
        self.assertEqual(MenuSection.objects.count(), 1)

        self.setUp() # reload the page
        self.assertIn(test_menusection.name, self.html)

    def test_menu_with_2_menusections(self):
        test_menusection_1 = self.test_menu.menusection_set.create(
                name='Test Menu Section 1')
        test_menusection_2 = self.test_menu.menusection_set.create(
                name='Test Menu Section 2')
        self.assertEqual(MenuSection.objects.count(), 2)

        self.setUp() # reload the page
        self.assertIn(test_menusection_1.name, self.html)
        self.assertIn(test_menusection_2.name, self.html)

class MenuSectionCreateViewTest(TestCase):

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
        cls.test_menu = cls.test_restaurant.menu_set.create(name='Test Menu')

    def setUp(self):

        # login as authorized user
        self.client.login(
            username='restaurant_admin_user', password='password')

        self.current_test_url = reverse('menus:menusection_create',
            kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': self.test_menu.slug,
                })
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = self.response.content.decode('utf-8')
        self.view = self.response.context['view']

    # view attributes
    def test_view_name(self):
        self.assertEqual(
            self.view.__class__.__name__, 'MenuSectionCreateView')

    def test_view_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'CreateView')

    def test_view_mixins(self):
        self.assertEqual(
            self.view.__class__.__bases__[0].__name__, 'UserPassesTestMixin')

    def test_view_model(self):
        self.assertEqual(self.context['view'].model.__name__, 'MenuSection')

    def test_view_form_class(self):
        self.assertEqual(self.context['view'].form_class.__name__,
                'MenuSectionCreateForm')

    def test_view_template_name(self):
        self.assertEqual(self.context['view'].template_name,
                'menus/menusection_create.html')

    # dispatch()
    def test_view_has_self_menu(self):
        self.assertEqual(self.view.menu, self.test_menu)

    # get_context_data()
    def test_view_context_contains_menu(self):
        self.assertTrue('menu' in self.context)

    def test_view_context_contains_correct_menu(self):
        self.assertEqual(self.context['menu'], self.test_menu)

    # get_initial()
    def test_view_get_initial_returns_menu(self):
        self.assertEqual(self.view.get_initial(), {'menu': self.test_menu})

    # request.GET
    def test_view_get_method_unauthenticated_user(self):
        self.client.logout()

        # request by unauthenticated user should redirect to login
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 302)
        redirect_url = urlparse(self.response.url)[2]
        self.assertEqual(redirect_url, reverse('login'))

    def test_view_get_method_authenticated_but_unauthorized_user(self):
        self.client.login(username='test_user', password='password')

        # request by unauthorized user should return 403
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.assertEqual(self.response.status_code, 403)

    def test_view_get_authorized_user(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertIn(
                "Please enter the information for your new menu section:",
                self.html)

    # request.POST
    def test_view_post_method_unauthenticated_user(self):
        self.client.logout()

        # get menusection count before attempting to post data
        old_menusection_count = MenuSection.objects.count()

        # attempt to create new menusection via POST
        self.response = self.client.post(self.current_test_url,
                kwargs = {
                    'menu': self.test_menu.pk,
                    'name': 'Test Menu Section',
                    })

        # user is redirected to login page
        self.assertEqual(self.response.status_code, 302)
        redirect_url = urlparse(self.response.url)[2]
        self.assertEqual(redirect_url, reverse('login'))

        # menusection count should be unchanged
        new_menusection_count = MenuSection.objects.count()
        self.assertEqual(old_menusection_count, new_menusection_count)

    def test_view_post_method_authenticated_but_unauthorized_user(self):
        self.client.login(username='test_user', password='password')

        # get menusection count before attempting to post data
        old_menusection_count = MenuSection.objects.count()

        # attempt to create new menusection via POST
        self.response = self.client.post(self.current_test_url,
                kwargs = {
                    'menu': self.test_menu.pk,
                    'name': 'Test Menu Section',
                    })

        # menusection count should be unchanged
        new_menusection_count = MenuSection.objects.count()
        self.assertEqual(old_menusection_count, new_menusection_count)

    def test_view_post_method_authorized_user(self):

        new_menusection_name = 'Test Menu Section'
        new_menusection_slug = slugify(new_menusection_name)

        # get menusection count before attempting to post data
        old_menusection_count = MenuSection.objects.count()

        # create new menusection via POST
        self.response = self.client.post(self.current_test_url, {
                    'menu': self.test_menu.pk,
                    'name': new_menusection_name})
        self.html = self.response.content.decode('utf-8')

        # menusection object count increased by 1
        new_menusection_count = MenuSection.objects.count()
        self.assertEqual(old_menusection_count + 1, new_menusection_count)

        # user is redirected to new menusection_detail
        new_menusection = MenuSection.objects.get(
                menu=self.test_menu,
                slug=new_menusection_slug)
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse(
            'menus:menusection_detail', kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': self.test_menu.slug,
                'menusection_slug': new_menusection_slug,
            }))

        # page loads successfully and uses proper template and expected text
        self.response = self.client.get(self.response.url)
        self.html = self.response.content.decode('utf-8')
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'menus/menusection_detail.html')
        self.assertIn("This section has no items.", self.html)

    def test_view_validation_post_method_duplicate_post_attempt_by_authorized_user_should_fail(self):

        # get menusection count before attempting to post data
        old_menusection_count = MenuSection.objects.count()

        # create new menusection via POST
        self.response = self.client.post(self.current_test_url, {
                    'menu': self.test_menu.pk,
                    'name': 'Test Menu Section',
                    })

        # menusection object count increased by 1
        new_menusection_count = MenuSection.objects.count()
        self.assertEqual(old_menusection_count + 1, new_menusection_count)

        # get menusection count before attempting to post data
        old_menusection_count = MenuSection.objects.count()

        # attempt to create duplicate menusection via POST
        self.response = self.client.post(self.current_test_url, {
                    'menu': self.test_menu.pk,
                    'name': 'Test Menu Section',
                    })
        self.html = self.response.content.decode('utf-8')
        self.assertIn("This name is too similar", self.html)

        # menusection object count has not changed
        new_menusection_count = MenuSection.objects.count()
        self.assertEqual(old_menusection_count, new_menusection_count)

class MenuSectionDetailViewTest(TestCase):

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
        cls.test_menu = cls.test_restaurant.menu_set.create(name='Test Menu')

        cls.test_menusection = \
            cls.test_menu.menusection_set.create(name='Test Menu Section')

    def setUp(self):

        # login as authorized user
        self.client.login(
            username='restaurant_admin_user', password='password')

        self.current_test_url = reverse('menus:menusection_detail',
            kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': self.test_menu.slug,
                'menusection_slug': self.test_menusection.slug,
                })
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = self.response.content.decode('utf-8')
        self.view = self.response.context['view']

    # view attributes
    def test_view_name(self):
        self.assertEqual(
            self.view.__class__.__name__, 'MenuSectionDetailView')

    def test_view_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'DetailView')

    def test_view_model(self):
        self.assertEqual(self.context['view'].model.__name__, 'MenuSection')

    def test_view_slug_url_kwarg(self):
        self.assertEqual(self.context['view'].slug_url_kwarg,
            'menusection_slug')

    # request.GET
    def test_view_get_method_unauthenticated_user(self):
        self.assertEqual(self.response.status_code, 200)

    # bad kwargs
    def test_view_bad_kwargs_menusection_slug(self):
        self.current_test_url = reverse('menus:menusection_detail',
            kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': self.test_menu.slug,
                'menusection_slug': 'bad-menusection-slug',
                })
        self.response = self.client.get(self.current_test_url)
        self.assertEqual(self.response.status_code, 404)
