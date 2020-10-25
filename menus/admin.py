from django.contrib import admin

from .models import Menu, MenuSection, MenuItem

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

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']

    class Meta:
        model = MenuItem

