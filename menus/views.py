from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Menu
from restaurants.models import Restaurant

class MenuDetailView(DetailView):
    model = Menu
