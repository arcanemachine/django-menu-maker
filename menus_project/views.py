from django.http import HttpResponse
from django.shortcuts import render

def hello_world(request):
    return HttpResponse(f"Hello, {request.resolver_match.namespace}:"\
            "{request.resolver_match.view_name}!")

def root(request):
    return render(request, 'root.html')
