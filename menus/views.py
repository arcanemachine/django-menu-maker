from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from .forms import MenuSectionCreateForm
from .models import Menu, MenuSection
from restaurants.models import Restaurant

def menus_root(request, restaurant_slug):
    return HttpResponseRedirect(reverse('restaurants:restaurant_detail',
        kwargs = {'restaurant_slug': restaurant_slug}))

class MenuDetailView(DetailView):
    model = Menu
    slug_url_kwarg = 'menu_slug'

    def get_object(self):
        return get_object_or_404(Menu,
            restaurant__slug=self.kwargs['restaurant_slug'],
            slug=self.kwargs['menu_slug'])

class MenuSectionCreateView(UserPassesTestMixin, CreateView):
    model = MenuSection
    form_class = MenuSectionCreateForm
    template_name = 'menus/menusection_create.html'

    def dispatch(self, request, *args, **kwargs):
        self.menu = get_object_or_404(Menu,
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
    slug_url_kwarg = 'menusection_slug'

