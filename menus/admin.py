from django.contrib import admin

from .models import Menu, MenuSection

#admin.site.register(Menu)
#admin.site.register(MenuSection)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'pk')
    readonly_fields = ['slug']

    class Meta:
        model = Menu

@admin.register(MenuSection)
class MenuSectionAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']

    class Meta:
        model = MenuSection
