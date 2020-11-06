from django.shortcuts import render
from rest_framework import generics

from .serializers import RestaurantSerializer
from restaurants.models import Restaurant

class RestaurantList(generics.ListCreateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
