from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView, ListView

from .models import Menu, MenuSection
from restaurants.models import Restaurant

class MenuDetailView(DetailView):
    model = Menu
    slug_url_kwarg = 'menu_slug'

    def get_object(self):
        return Menu.objects.get(
            restaurant__slug=self.kwargs['restaurant_slug'],
            slug=self.kwargs['menu_slug'])

class MenuSectionCreateView(CreateView):
    model = MenuSection
    fields = ['name']
