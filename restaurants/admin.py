from django.contrib import admin

from .models import Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']

    class Meta:
        model = Restaurant
