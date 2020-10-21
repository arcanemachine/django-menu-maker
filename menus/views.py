#from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .models import Menu

class RestaurantMenuListView(ListView):
    #model = Menu
    template_name = 'menus/restaurant_menu_list.html'

    def get_queryset(self):
        return Menu.objects.all()

class MenuDetailView(DetailView):
    model = Menu
