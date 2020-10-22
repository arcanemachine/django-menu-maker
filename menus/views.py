from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Menu
from restaurants.models import Restaurant

class RestaurantMenuListView(ListView):
    template_name = 'menus/restaurant_menu_list.html'
    context_object_name = 'menus'

    def dispatch(self, request, *args, **kwargs):
        self.restaurant = \
            get_object_or_404(Restaurant, slug=self.kwargs['restaurant_slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurant'] = self.restaurant
        return context

    def get_queryset(self):
        return Menu.objects.filter(
                restaurant__slug=self.kwargs['restaurant_slug'])

class MenuDetailView(DetailView):
    model = Menu
