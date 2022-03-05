def get_next_url(request, url):
    if request.GET.get('next', None):
        return request.GET['next']
    return url
