from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from restaurants.models import Restaurant

class Menu(models.Model):

    THEME_CHOICES = [
        ('default', "Default"),
        ('secondary', "Secondary"),
        ]

    restaurant = models.ForeignKey('restaurants.Restaurant',
            on_delete=models.CASCADE,
            null=True)

    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, null=True)
    theme = models.CharField(
            max_length=32, choices=THEME_CHOICES, default='default')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        # do not allow a restaurant to have duplicate menu slugs
        existing_menus = Menu.objects.filter(
                restaurant=self.restaurant,
                slug=self.slug)
        if existing_menus.count():
            if existing_menus.first() != self or existing_menus.last() != self:
                raise ValidationError(
                    "This name is too similar to one of this restaurant's "\
                    "existing menu names.")

    def get_absolute_url(self):
        return reverse('menus:menu_detail',
                kwargs={
                    'restaurant_slug': self.restaurant.slug,
                    'menu_slug': self.slug,
                    })

    def save(self, *args, **kwargs):
        if not self.slug == slugify(self.name):
            self.slug = slugify(self.name)
        self.clean()
        super().save(*args, **kwargs)

class MenuSection(models.Model):

    menu = models.ForeignKey('Menu', on_delete=models.CASCADE)

    name = models.CharField(max_length=128, null=True)
    slug = models.SlugField(max_length=128, null=True)

    def __str__(self):
        return f"{self.menu.restaurant.name}: {self.menu.name} - {self.name}"

    def get_absolute_url(self):
        return reverse('menus:menusection_detail',
            kwargs = {
                'restaurant_slug': self.menu.restaurant.slug,
                'menu_slug': self.menu.slug,
                'menusection_slug': self.slug,
                })


    def clean(self):
        # do not allow a menu to have duplicate section slugs
        existing_menusections = MenuSection.objects.filter(
                menu=self.menu,
                slug=self.slug)
        if existing_menusections.count():
            if existing_menusections.first() != self \
                    or existing_menusections.last() != self:
                raise ValidationError(
                    "This name is too similar to one of this menu's "\
                    "existing section names.")

    def save(self, *args, **kwargs):
        if not self.slug == slugify(self.name):
            self.slug = slugify(self.name)
        self.clean()
        super().save(*args, **kwargs)

