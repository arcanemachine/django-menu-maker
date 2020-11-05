from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.edit import UpdateView

from .models import Restaurant
from menus_project import constants


class RestaurantListView(ListView):
    model = Restaurant
    context_object_name = 'restaurants'


class RestaurantCreateView(LoginRequiredMixin, CreateView):
    model = Restaurant
    fields = ('name',)
    success_message = "Restaurant Created: %(name)s"

    def dispatch(self, request, *args, **kwargs):
        # do not allow users to register too many restaurants
        if request.user.restaurant_set.count() >= \
                constants.MAX_RESTAURANTS_PER_USER  \
                and not request.user.is_staff:
            messages.error(
                request, constants.MAX_RESTAURANTS_PER_USER_ERROR_STRING)
            return super().get(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        self.object.admin_users.add(self.request.user)
        messages.success(
            self.request, self.success_message % self.object.__dict__)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'action_verb': 'Create'})
        return context


class RestaurantUpdateView(
        UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Restaurant
    fields = ('name',)
    success_message = "Restaurant Successfully Updated: %(name)s"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'action_verb': 'Update'})
        return context

    def get_initial(self):
        return {'name': self.get_object().name}

    def get_object(self):
        return get_object_or_404(
            Restaurant, slug=self.kwargs['restaurant_slug'])

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return self.request.user in \
            self.get_object().admin_users.all()


class RestaurantDetailView(DetailView):
    model = Restaurant
    slug_url_kwarg = 'restaurant_slug'
