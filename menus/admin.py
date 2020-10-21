from django.contrib import admin

from .models import Menu, MenuSection

#admin.site.register(Menu)
admin.site.register(MenuSection)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant')
    readonly_fields = ['slug']

    class Meta:
        model = Menu
