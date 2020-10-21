from django.http import HttpResponse
from django.shortcuts import render

def root(request):
    return render(request, 'root.html')
