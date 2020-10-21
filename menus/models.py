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
            related_name='menus',
            on_delete=models.CASCADE,
            null=True)

    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, null=True)
    theme = models.CharField(
            max_length=32, choices=THEME_CHOICES, default='default')

    def __str__(self):
        return self.name

    def clean(self):
        # do not allow duplicate menu names for a given restaurant
        existing_menus = Menu.objects.filter(
                restaurant=self.restaurant,
                name=self.name)
        if existing_menus.count():
            if existing_menus.first() != self or existing_menus.last() != self:
                raise ValidationError(
                    "This restaurant already has a menu with this name.")

    def get_absolute_url(self):
        return reverse('menus:menu_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.clean()
        if not self.slug == slugify(self.name):
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class MenuSection(models.Model):

    menu = models.ForeignKey(
        'Menu',
        on_delete=models.CASCADE)

    name = models.CharField(max_length=128, null=True)
    slug = models.SlugField(max_length=128, null=True)

    #image = models.ImageField()
