from django.views.generic import DetailView, ListView

from .models import Restaurant


class RestaurantListView(ListView):
    model = Restaurant
    context_object_name = 'restaurants'


class RestaurantDetailView(DetailView):
    model = Restaurant
    slug_url_kwarg = 'restaurant_slug'
