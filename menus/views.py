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
    template_name = 'menus/menusection_create.html'

    def dispatch(self, request, *args, **kwargs):
        self.menu = Menu.objects.get(
                restaurant__slug=self.kwargs['restaurant_slug'],
                slug=self.kwargs['menu_slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = self.menu
        return context

    def form_valid(self, form):
        form.instance.menu = self.menu
        return super().form_valid(form)
