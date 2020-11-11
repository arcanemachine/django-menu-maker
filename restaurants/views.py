from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView
from django.views.generic.edit import UpdateView

from .models import Restaurant
from menus_project import constants as c
from menus_project.permissions import UserHasRestaurantPermissionsMixin


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
                c.MAX_RESTAURANTS_PER_USER  \
                and not request.user.is_staff:
            messages.error(
                request, c.MAX_RESTAURANTS_PER_USER_ERROR_STRING)
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


class RestaurantDetailView(DetailView):
    model = Restaurant
    slug_url_kwarg = 'restaurant_slug'


class RestaurantUpdateView(
        UserHasRestaurantPermissionsMixin, SuccessMessageMixin, UpdateView):
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


class RestaurantDeleteView(UserHasRestaurantPermissionsMixin, DeleteView):
    model = Restaurant
    success_message = "The '%(name)s' restaurant has been deleted."
    success_url = reverse_lazy('users:user_detail')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super().delete(request, *args, **kwargs)

    def get_object(self):
        return get_object_or_404(
            Restaurant, slug=self.kwargs['restaurant_slug'])
