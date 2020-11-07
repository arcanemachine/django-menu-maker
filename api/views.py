from django.shortcuts import render
from rest_framework import viewsets

from .serializers import RestaurantSerializer
from .permissions import HasRestaurantPrivileges
from restaurants.models import Restaurant

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
