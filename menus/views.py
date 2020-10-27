from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView
from django.views.generic.edit import UpdateView

from .forms import MenuSectionCreateForm, MenuItemForm
from .models import Menu, MenuSection, MenuItem


def menus_root(request, restaurant_slug):
    return HttpResponseRedirect(
        reverse('restaurants:restaurant_detail', kwargs={
            'restaurant_slug': restaurant_slug}))


class MenuDetailView(DetailView):
    model = Menu

    def get_object(self):
        return get_object_or_404(
            Menu,
            restaurant__slug=self.kwargs['restaurant_slug'],
            slug=self.kwargs['menu_slug'])


class MenuSectionCreateView(UserPassesTestMixin, CreateView):
    model = MenuSection
    form_class = MenuSectionCreateForm
    template_name = 'menus/menusection_create.html'

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


class MenuItemCreateView(UserPassesTestMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm

    def dispatch(self, request, *args, **kwargs):
        self.menusection = get_object_or_404(
            MenuSection,
            menu__restaurant__slug=self.kwargs['restaurant_slug'],
            menu__slug=self.kwargs['menu_slug'],
            slug=self.kwargs['menusection_slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_verb'] = 'Create'
        context['menusection'] = self.menusection
        return context

    def get_initial(self):
        return {'menusection': self.menusection}

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


class MenuItemUpdateView(UserPassesTestMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_verb'] = 'Update'
        context['menusection'] = self.get_object().menusection
        return context

    def get_initial(self):
        return {'menusection': self.get_object().menusection}

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
