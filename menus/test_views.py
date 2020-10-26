from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from inspect import getfullargspec
from urllib.parse import urlparse

from . import views
from .models import Menu, MenuSection, MenuItem
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
        self.response = self.client.get(self.response.url)
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

    def test_view_model_name(self):
        self.assertEqual(self.context['view'].model.__name__, 'Menu')

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

    # template - menusection count
    def test_menu_with_0_menusections(self):
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

    # bad kwargs
    def test_view_bad_kwargs(self):
        for i in range(2):
            self.current_test_url = reverse('menus:menu_detail',
                kwargs = {
                    'restaurant_slug': self.test_restaurant.slug \
                        if i != 0 else 'bad-restaurant-slug',
                    'menu_slug': self.test_menu.slug \
                        if i != 1 else 'bad-menu-slug',
                    })
            self.response = self.client.get(self.current_test_url)
            self.assertEqual(self.response.status_code, 404)

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

    def test_view_model_name(self):
        self.assertEqual(self.context['view'].model.__name__, 'MenuSection')

    def test_view_form_class(self):
        self.assertEqual(self.context['view'].form_class.__name__,
            'MenuSectionCreateForm')

    def test_view_template_name(self):
        self.assertEqual(self.context['view'].template_name,
            'menus/menusection_create.html')

    # dispatch()
    def test_view_method_dispatch_self_has_attribute_menu(self):
        self.assertTrue(hasattr(self.view, 'menu'))

    def test_view_method_dispatch_self_has_correct_menu(self):
        self.assertEqual(self.view.menu, self.test_menu)

    # get_context_data()
    def test_view_context_contains_menu(self):
        self.assertTrue('menu' in self.context)

    def test_view_context_contains_correct_menu(self):
        self.assertEqual(self.context['menu'], self.test_menu)

    # get_initial()
    def test_view_method_get_initial_returns_menu(self):
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

        # user should receive HTTP 403
        self.assertEqual(self.response.status_code, 403)

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

    # bad kwargs
    def test_view_bad_kwargs(self):
        for i in range(2):
            self.current_test_url = reverse('menus:menusection_create',
                kwargs = {
                    'restaurant_slug': self.test_restaurant.slug \
                        if i != 0 else 'bad-restaurant-slug',
                    'menu_slug': self.test_menu.slug \
                        if i != 1 else 'bad-menu-slug',
                    })
            self.response = self.client.get(self.current_test_url)
            self.assertEqual(self.response.status_code, 404)

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

        # create test menusection
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

    def test_view_model_name(self):
        self.assertEqual(self.context['view'].model.__name__, 'MenuSection')

    # request.GET
    def test_view_get_method_unauthenticated_user(self):
        self.assertEqual(self.response.status_code, 200)

    # template
    def test_template_non_restaurant_admin_user_cannot_view_link_to_add_menuitem(self):
        self.client.logout()
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = self.response.content.decode('utf-8')
        self.assertNotIn('Add New Menu Item', self.html)

    def test_template_restaurant_admin_user_can_view_link_to_add_menuitem(self):
        self.assertIn('Add New Menu Item', self.html)

    # bad kwargs
    def test_view_bad_kwargs(self):
        for i in range(3):
            self.current_test_url = reverse('menus:menusection_detail',
                kwargs = {
                    'restaurant_slug': self.test_restaurant.slug \
                        if i != 0 else 'bad-restaurant-slug',
                    'menu_slug': self.test_menu.slug \
                        if i != 1 else 'bad-menu-slug',
                    'menusection_slug': self.test_menusection.slug \
                        if i != 2 else 'bad-menusection-slug',
                    })
            self.response = self.client.get(self.current_test_url)
            self.assertEqual(self.response.status_code, 404)

class MenuItemCreateViewTest(TestCase):

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

        # create test menusection
        cls.test_menusection = \
            cls.test_menu.menusection_set.create(name='Test Menu Section')

    def setUp(self):

        # login as authorized user
        self.client.login(
            username='restaurant_admin_user', password='password')

        self.current_test_url = reverse('menus:menuitem_create',
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
            self.view.__class__.__name__, 'MenuItemCreateView')

    def test_view_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'CreateView')

    def test_view_mixins(self):
        self.assertEqual(
            self.view.__class__.__bases__[0].__name__, 'UserPassesTestMixin')

    def test_view_model_name(self):
        self.assertEqual(self.context['view'].model.__name__, 'MenuItem')

    def test_view_form_class(self):
        self.assertEqual(self.context['view'].form_class.__name__,
            'MenuItemForm')

    # dispatch()
    def test_view_method_dispatch_self_has_attribute_menusection(self):
        self.assertTrue(hasattr(self.view, 'menusection'))

    def test_view_method_dispatch_self_has_correct_menusection(self):
        self.assertEqual(self.view.menusection, self.test_menusection)

    # get_context_data()
    def test_view_context_has_action_verb(self):
        self.assertTrue('action_verb' in self.context)

    def test_view_context_has_correct_action_verb(self):
        self.assertEqual(self.context['action_verb'], 'Create')

    def test_view_context_has_menusection(self):
        self.assertTrue('menusection' in self.context)

    def test_view_context_has_correct_menusection(self):
        self.assertEqual(self.context['menusection'], self.test_menusection)

    # get_initial()
    def test_view_method_get_initial_returns_menusection(self):
        self.assertEqual(self.view.get_initial(),
            {'menusection': self.test_menusection})

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

    def test_view_get_method_authorized_user(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertIn(
            "Please enter the information for your menu item:",
            self.html)

    # request.POST
    def test_view_post_method_unauthenticated_user(self):
        self.client.logout()

        # get menusection count before attempting to post data
        old_menuitem_count = MenuItem.objects.count()

        # attempt to create new menusection via POST
        self.response = self.client.post(self.current_test_url,
            kwargs = {
                'menusection': self.test_menusection.pk,
                'name': 'Test Menu Item',
                'description': 'Test Menu Item Description',
                })

        # user is redirected to login page
        self.assertEqual(self.response.status_code, 302)
        redirect_url = urlparse(self.response.url)[2]
        self.assertEqual(redirect_url, reverse('login'))

        # menusection count should be unchanged
        new_menuitem_count = MenuItem.objects.count()
        self.assertEqual(old_menuitem_count, new_menuitem_count)

    def test_view_post_method_authenticated_but_unauthorized_user(self):
        self.client.login(username='test_user', password='password')

        # get menusection count before attempting to post data
        old_menuitem_count = MenuItem.objects.count()

        # attempt to create new menusection via POST
        self.response = self.client.post(self.current_test_url, {
                'menusection': self.test_menusection.pk,
                'name': 'Test Menu Item',
                'description': 'Test Menu Item Description',
                })

        # menusection count should be unchanged
        new_menuitem_count = MenuItem.objects.count()
        self.assertEqual(old_menuitem_count, new_menuitem_count)

        # user should receive HTTP 403
        self.assertEqual(self.response.status_code, 403)


    def test_view_post_method_authorized_user(self):

        new_menuitem_name = 'Test Menu Item'
        new_menuitem_slug = slugify(new_menuitem_name)

        # get menusection count before attempting to post data
        old_menuitem_count = MenuItem.objects.count()

        # create new menusection via POST
        self.response = self.client.post(self.current_test_url, {
            'menusection': self.test_menusection.pk,
            'name': 'Test Menu Item',
            'description': 'Test Menu Item Description',
            })
        self.html = self.response.content.decode('utf-8')

        # menusection object count increased by 1
        new_menuitem_count = MenuItem.objects.count()
        self.assertEqual(old_menuitem_count + 1, new_menuitem_count)

        # user is redirected to new menusection_detail
        new_menuitem = MenuItem.objects.get(
            menusection=self.test_menusection,
            slug=new_menuitem_slug)
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse(
            'menus:menuitem_detail', kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': self.test_menu.slug,
                'menusection_slug': self.test_menusection.slug,
                'menuitem_slug': new_menuitem_slug,
                }))

        # page loads successfully and uses proper template and expected text
        self.response = self.client.get(self.response.url)
        self.html = self.response.content.decode('utf-8')
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'menus/menuitem_detail.html')
        self.assertIn(f"{new_menuitem.description}", self.html)


    ### VALIDATION ###

    def test_view_validation_post_method_duplicate_post_attempt_by_authorized_user_should_fail(self):

        # get menusection count before attempting to post data
        old_menuitem_count = MenuItem.objects.count()

        # create new menusection via POST
        self.response = self.client.post(self.current_test_url, {
            'menusection': self.test_menusection.pk,
            'name': 'Test Menu Item',
            'description': 'Test Menu Item Description',
            })

        # menusection object count increased by 1
        new_menuitem_count = MenuItem.objects.count()
        self.assertEqual(old_menuitem_count + 1, new_menuitem_count)

        # get menusection count before attempting to post data
        old_menuitem_count = MenuItem.objects.count()

        # attempt to create duplicate menusection via POST
        self.response = self.client.post(self.current_test_url, {
            'menusection': self.test_menusection.pk,
            'name': 'Test Menu Item',
            'description': 'Test Menu Item Description',
            })

        # returns template for menus:menusection_create, with error message
        self.html = self.response.content.decode('utf-8')
        self.assertIn("This name is too similar", self.html)

        # menusection object count has not changed
        new_menuitem_count = MenuItem.objects.count()
        self.assertEqual(old_menuitem_count, new_menuitem_count)

    # bad kwargs
    def test_view_bad_kwargs(self):
        for i in range(3):
            self.current_test_url = reverse('menus:menuitem_create',
                kwargs = {
                    'restaurant_slug': self.test_restaurant.slug \
                        if i != 0 else 'bad-restaurant-slug',
                    'menu_slug': self.test_menu.slug \
                        if i != 1 else 'bad-menu-slug',
                    'menusection_slug': self.test_menusection.slug \
                        if i != 2 else 'bad-menusection-slug',
                    })
            self.response = self.client.get(self.current_test_url)
            self.assertEqual(self.response.status_code, 404)

class MenuItemDetailViewTest(TestCase):

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

        # create test menusection
        cls.test_menusection = \
            cls.test_menu.menusection_set.create(name='Test Menu Section')

        # create test menuitem
        cls.test_menuitem = \
            cls.test_menusection.menuitem_set.create(name='Test Menu Item')

    def setUp(self):

        # login as authorized user
        self.client.login(
            username='restaurant_admin_user', password='password')

        self.current_test_url = reverse('menus:menuitem_detail',
            kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': self.test_menu.slug,
                'menusection_slug': self.test_menusection.slug,
                'menuitem_slug': self.test_menuitem.slug,
                })
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = self.response.content.decode('utf-8')
        self.view = self.response.context['view']

    # view attributes
    def test_view_name(self):
        self.assertEqual(
            self.view.__class__.__name__, 'MenuItemDetailView')

    def test_view_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'DetailView')

    def test_view_model_name(self):
        self.assertEqual(self.context['view'].model.__name__, 'MenuItem')

    # get_object()
    def test_view_method_get_object(self):
        self.assertEqual(self.view.get_object(), self.test_menuitem)

    # request.GET
    def test_view_get_method_unauthenticated_user(self):
        self.assertEqual(self.response.status_code, 200)

    # bad kwargs
    def test_view_bad_kwargs(self):
        for i in range(4):
            self.current_test_url = reverse('menus:menuitem_detail',
                kwargs = {
                    'restaurant_slug': self.test_restaurant.slug \
                        if i != 0 else 'bad-restaurant-slug',
                    'menu_slug': self.test_menu.slug \
                        if i != 1 else 'bad-menu-slug',
                    'menusection_slug': self.test_menusection.slug \
                        if i != 2 else 'bad-menusection-slug',
                    'menuitem_slug': 'bad-menuitem-slug' \
                        if i != 3 else 'bad-menuitem-slug',
                    })
            self.response = self.client.get(self.current_test_url)
            self.assertEqual(self.response.status_code, 404)

class MenuItemUpdateViewTest(TestCase):

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

        # create test menusection
        cls.test_menusection = \
            cls.test_menu.menusection_set.create(name='Test Menu Section')

    def setUp(self):

        # create test menuitem
        self.test_menuitem = \
            self.test_menusection.menuitem_set.create(name='Test Menu Item')

        # login as authorized user
        self.client.login(
            username='restaurant_admin_user', password='password')

        self.current_test_url = reverse('menus:menuitem_update',
            kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': self.test_menu.slug,
                'menusection_slug': self.test_menusection.slug,
                'menuitem_slug': self.test_menuitem.slug,
                })
        self.response = self.client.get(self.current_test_url)
        self.context = self.response.context
        self.html = self.response.content.decode('utf-8')
        self.view = self.response.context['view']

    # view attributes
    def test_view_name(self):
        self.assertEqual(
            self.view.__class__.__name__, 'MenuItemUpdateView')

    def test_view_parent_class_name(self):
        self.assertEqual(
            self.view.__class__.__bases__[-1].__name__, 'UpdateView')

    def test_view_mixins(self):
        self.assertEqual(
            self.view.__class__.__bases__[0].__name__, 'UserPassesTestMixin')

    def test_view_model_name(self):
        self.assertEqual(self.context['view'].model.__name__, 'MenuItem')

    def test_view_form_class(self):
        self.assertEqual(self.context['view'].form_class.__name__,
            'MenuItemForm')

    # get_context_data()
    def test_view_context_has_action_verb(self):
        self.assertTrue('action_verb' in self.context)

    def test_view_context_has_correct_action_verb(self):
        self.assertEqual(self.context['action_verb'], 'Update')

    def test_view_context_has_menusection(self):
        self.assertTrue('menusection' in self.context)

    def test_view_context_has_correct_menusection(self):
        self.assertEqual(self.context['menusection'], self.test_menusection)

    # get_initial()
    def test_view_method_get_initial_returns_menusection(self):
        self.assertEqual(self.view.get_initial(),
            {'menusection': self.test_menusection})

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

    def test_view_get_method_authorized_user(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertIn(
            "Please enter the information for your menu item:",
            self.html)

    # request.POST
    def test_view_post_method_unauthenticated_user(self):
        self.client.logout()

        old_menuitem_name = self.test_menuitem.name
        old_menuitem_description = self.test_menuitem.description
        new_menuitem_name = 'New Test Menu Item'
        new_menuitem_description = 'New Test Menu Item Description'

        # attempt to update self.test_menuitem via POST
        self.response = self.client.post(self.current_test_url, {
            'menusection': self.test_menuitem.menusection.pk,
            'name': new_menuitem_name,
            'description': new_menuitem_description,
            })

        # user is redirected to login page
        self.assertEqual(self.response.status_code, 302)
        redirect_url = urlparse(self.response.url)[2]
        self.assertEqual(redirect_url, reverse('login'))

        # self.test_menuitem is unchanged
        self.test_menuitem.refresh_from_db()
        self.assertEqual(self.test_menuitem.name, old_menuitem_name)
        self.assertEqual(
                self.test_menuitem.description, old_menuitem_description)

    def test_view_post_method_authenticated_but_unauthorized_user(self):
        self.client.login(username='test_user', password='password')

        old_menuitem_name = self.test_menuitem.name
        old_menuitem_description = self.test_menuitem.description
        new_menuitem_name = 'New Test Menu Item'
        new_menuitem_description = 'New Test Menu Item Description'

        # attempt to update self.test_menuitem via POST
        self.response = self.client.post(self.current_test_url, {
            'menusection': self.test_menuitem.menusection.pk,
            'name': new_menuitem_name,
            'description': new_menuitem_description,
            })

        # self.test_menuitem is unchanged
        self.test_menuitem.refresh_from_db()
        self.assertEqual(self.test_menuitem.name, old_menuitem_name)
        self.assertEqual(
                self.test_menuitem.description, old_menuitem_description)

        # user should receive HTTP 403
        self.assertEqual(self.response.status_code, 403)

    def test_view_post_method_authorized_user(self):

        old_menuitem_name = self.test_menuitem.name
        old_menuitem_description = self.test_menuitem.description
        old_menuitem_slug = self.test_menuitem.slug

        new_menuitem_name = 'New Test Menu Item'
        new_menuitem_description = 'New Test Menu Item Description'
        new_menuitem_slug = slugify(new_menuitem_name)

        # get menuitem count before attempting to post data
        old_menuitem_count = MenuItem.objects.count()

        # update self.test_menuitem via POST
        self.response = self.client.post(self.current_test_url, {
            'menusection': self.test_menuitem.menusection.pk,
            'name': new_menuitem_name,
            'description': new_menuitem_description,
            })
        self.html = self.response.content.decode('utf-8')

        # menuitem object count has not changed
        new_menuitem_count = MenuItem.objects.count()
        self.assertEqual(old_menuitem_count, new_menuitem_count)

        # self.test_menuitem has been updated with new values
        self.test_menuitem.refresh_from_db()
        self.assertEqual(self.test_menuitem.name, new_menuitem_name)
        self.assertEqual(
            self.test_menuitem.description, new_menuitem_description)
        self.assertEqual(self.test_menuitem.slug, new_menuitem_slug)

        # user is redirected to menuitem_detail
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.response.url, reverse(
            'menus:menuitem_detail', kwargs = {
                'restaurant_slug': self.test_restaurant.slug,
                'menu_slug': self.test_menu.slug,
                'menusection_slug': self.test_menusection.slug,
                'menuitem_slug': new_menuitem_slug,
                }))

        # menuitem_detail loads successfully and uses proper template
        self.response = self.client.get(self.response.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'menus/menuitem_detail.html')

        # menuitem_detail contains new menuitem values
        self.html = self.response.content.decode('utf-8')
        self.assertIn(f"{self.test_menuitem.name}", self.html)
        self.assertIn(f"{self.test_menuitem.description}", self.html)

    def test_view_validation_postmethod_duplicate_post_attempt_by_authorized_user_should_fail(self):

        self.test_menuitem_2 = self.test_menusection.menuitem_set.create(
                name='New Test Menu Item',
                description='New Test Menu Description')

        old_menuitem_name = self.test_menuitem.name
        old_menuitem_description = self.test_menuitem.description
        old_menuitem_slug = self.test_menuitem.slug

        new_menuitem_name = self.test_menuitem_2.name
        new_menuitem_description = self.test_menuitem_2.description
        new_menuitem_slug = self.test_menuitem_2.slug

        # get menuitem count before attempting to post data
        old_menuitem_count = MenuItem.objects.count()

        # update self.test_menuitem via POST
        self.response = self.client.post(self.current_test_url, {
            'menusection': self.test_menuitem.menusection.pk,
            'name': new_menuitem_name,
            'description': new_menuitem_description,
            })

        # returns template for menus:menuitem_update, with error message
        self.html = self.response.content.decode('utf-8')
        self.assertIn("This name is too similar", self.html)

        # self.test_menuitem still has original values
        self.test_menuitem.refresh_from_db()
        self.assertEqual(self.test_menuitem.name, old_menuitem_name)
        self.assertEqual(
            self.test_menuitem.description, old_menuitem_description)
        self.assertEqual(self.test_menuitem.slug, old_menuitem_slug)

    # bad kwargs
    def test_view_bad_kwargs(self):
        for i in range(3):
            self.current_test_url = reverse('menus:menuitem_update',
                kwargs = {
                    'restaurant_slug': self.test_restaurant.slug \
                        if i != 0 else 'bad-restaurant-slug',
                    'menu_slug': self.test_menu.slug \
                        if i != 1 else 'bad-menu-slug',
                    'menusection_slug': self.test_menusection.slug \
                        if i != 2 else 'bad-menusection-slug',
                    'menuitem_slug': self.test_menuitem.slug \
                        if i != 3 else 'bad-menuitem-slug',
                    })
            self.response = self.client.get(self.current_test_url)
            self.assertEqual(self.response.status_code, 404)


