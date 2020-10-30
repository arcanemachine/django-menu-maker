from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, DeleteView
from django.views.generic.edit import UpdateView

from .forms import MenuForm, MenuSectionCreateForm, MenuItemForm
from .models import Menu, MenuSection, MenuItem
from restaurants.models import Restaurant


def menus_root(request, restaurant_slug):
    return HttpResponseRedirect(
        reverse('restaurants:restaurant_detail', kwargs={
            'restaurant_slug': restaurant_slug}))


class MenuCreateView(
        UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Menu
    form_class = MenuForm
    success_message = "Menu Created: %(name)s"

    def dispatch(self, request, *args, **kwargs):
        self.restaurant = get_object_or_404(
            Restaurant, slug=self.kwargs['restaurant_slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'action_verb': 'Create',
            'restaurant': self.restaurant})
        return context

    def get_initial(self):
        return {'restaurant': self.restaurant}

    def test_func(self):
        return self.request.user in self.restaurant.admin_users.all()


class MenuDetailView(DetailView):
    model = Menu

    def get_object(self):
        return get_object_or_404(
            Menu,
            restaurant__slug=self.kwargs['restaurant_slug'],
            slug=self.kwargs['menu_slug'])


class MenuUpdateView(
        UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Menu
    form_class = MenuForm
    success_message = "Menu Successfully Updated: %(name)s"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'action_verb': 'Update',
            'restaurant': self.get_object().restaurant,
            'menu': self.get_object()})
        return context

    def get_initial(self):
        return {
            'restaurant': self.get_object().restaurant,
            'name': self.get_object().name}

    def get_object(self):
        return get_object_or_404(
            Menu,
            restaurant__slug=self.kwargs['restaurant_slug'],
            slug=self.kwargs['menu_slug'])

    def test_func(self):
        return self.request.user in \
            self.get_object().restaurant.admin_users.all()


class MenuDeleteView(UserPassesTestMixin, DeleteView):
    model = Menu
    success_message = "The '%(name)s' menu has been deleted."

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super().delete(request, *args, **kwargs)

    def get_object(self):
        return get_object_or_404(
            Menu,
            restaurant__slug=self.kwargs['restaurant_slug'],
            slug=self.kwargs['menu_slug'])

    def get_success_url(self):
        return self.object.restaurant.get_absolute_url()

    def test_func(self):
        return self.request.user in \
            self.get_object().restaurant.admin_users.all()

class MenuSectionCreateView(
        UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = MenuSection
    form_class = MenuSectionCreateForm
    template_name = 'menus/menusection_create.html'
    success_message = "Menu Section Created: %(name)s"

    def dispatch(self, request, *args, **kwargs):
        self.menu = get_object_or_404(
            Menu,
            restaurant__slug=self.kwargs['restaurant_slug'],
            slug=self.kwargs['menu_slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = self.menu
        return context

    def get_initial(self):
        return {'menu': self.menu}

    def test_func(self):
        return self.request.user in self.menu.restaurant.admin_users.all()


class MenuSectionDetailView(DetailView):
    model = MenuSection

    def get_object(self):
        return get_object_or_404(
            MenuSection,
            menu__restaurant__slug=self.kwargs['restaurant_slug'],
            menu__slug=self.kwargs['menu_slug'],
            slug=self.kwargs['menusection_slug'])


class MenuItemCreateView(
        UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    success_message = "Menu Item Created: %(name)s"

    def dispatch(self, request, *args, **kwargs):
        self.menusection = get_object_or_404(
            MenuSection,
            menu__restaurant__slug=self.kwargs['restaurant_slug'],
            menu__slug=self.kwargs['menu_slug'],
            slug=self.kwargs['menusection_slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'action_verb': 'Create',
            'menusection': self.menusection})
        return context

    def get_initial(self):
        return {'menusection': self.menusection}

    def get_success_url(self):
        return self.object.menusection.get_absolute_url()

    def test_func(self):
        return self.request.user in \
            self.menusection.menu.restaurant.admin_users.all()


class MenuItemDetailView(DetailView):
    model = MenuItem

    def get_object(self):
        return get_object_or_404(
            MenuItem,
            menusection__menu__restaurant__slug=self.kwargs['restaurant_slug'],
            menusection__menu__slug=self.kwargs['menu_slug'],
            menusection__slug=self.kwargs['menusection_slug'],
            slug=self.kwargs['menuitem_slug'])


class MenuItemUpdateView(
        UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    success_message = "Menu Item Successfully Updated: %(name)s"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'action_verb': 'Update',
            'menusection': self.get_object().menusection,
            'menuitem': self.get_object()})
        return context

    def get_initial(self):
        return {
            'menusection': self.get_object().menusection,
            'name': self.get_object().name,
            'description': self.get_object().description}

    def get_object(self):
        return get_object_or_404(
            MenuItem,
            menusection__menu__restaurant__slug=self.kwargs['restaurant_slug'],
            menusection__menu__slug=self.kwargs['menu_slug'],
            menusection__slug=self.kwargs['menusection_slug'],
            slug=self.kwargs['menuitem_slug'])

    def test_func(self):
        return self.request.user in \
            self.get_object().menusection.menu.restaurant.admin_users.all()


class MenuItemDeleteView(UserPassesTestMixin, DeleteView):
    model = MenuItem
    success_message = "'%(name)s' has been deleted from the menu."

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super().delete(request, *args, **kwargs)

    def get_object(self):
        return get_object_or_404(
            MenuItem,
            menusection__menu__restaurant__slug=self.kwargs['restaurant_slug'],
            menusection__menu__slug=self.kwargs['menu_slug'],
            menusection__slug=self.kwargs['menusection_slug'],
            slug=self.kwargs['menuitem_slug'])

    def get_success_url(self):
        return self.object.menusection.get_absolute_url()

    def test_func(self):
        return self.request.user in \
            self.get_object().menusection.menu.restaurant.admin_users.all()
