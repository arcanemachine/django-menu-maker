from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .models import Restaurant

class RestaurantListView(ListView):
    model = Restaurant
    context_object_name = 'restaurants'

class RestaurantDetailView(DetailView):
    model = Restaurant
