import os

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from menus_project import constants


def menu_upload_to(instance, filename):
    base, extension = os.path.splitext(filename)
    extension = extension.lower()
    return "img/restaurants/"\
        f"{instance.restaurant.pk}-{instance.restaurant.slug}/"\
        f"menu-{instance.pk}-{instance.slug}{extension}"


class Menu(models.Model):

    THEME_CHOICES = [
        ('default', "Default"),
        ('secondary', "Secondary")]

    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE)

    name = models.CharField(max_length=128, default=None, blank=False)
    slug = models.SlugField(max_length=128)
    image = models.ImageField(
        help_text="An image or logo for this menu (optional)",
        upload_to=menu_upload_to, blank=True, null=True)
    description = models.CharField(max_length=256, blank=True, null=True)
    theme = models.CharField(
        max_length=32,
        choices=THEME_CHOICES,
        default='default')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"

    def clean(self):
        # do not allow slugs to be reserved keywords
        if self.slug in constants.RESERVED_KEYWORDS:
            raise ValidationError(constants.RESERVED_KEYWORD_ERROR_STRING)

        # do not allow a restaurant to have duplicate menu slugs
        menus_with_same_slug = Menu.objects.filter(
            restaurant=self.restaurant,
            slug=slugify(self.name))
        if menus_with_same_slug.count():
            if menus_with_same_slug.first() != self \
                    or menus_with_same_slug.last() != self:
                raise ValidationError(
                    "This name is too similar to one of this restaurant's "
                    "existing menu names.")

    def get_absolute_url(self):
        return reverse('menus:menu_detail', kwargs={
            'restaurant_slug': self.restaurant.slug,
            'menu_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug == slugify(self.name):
            self.slug = slugify(self.name)
        self.clean()
        super().save(*args, **kwargs)


def menusection_upload_to(instance, filename):
    base, extension = os.path.splitext(filename)
    extension = extension.lower()
    return "img/restaurants/"\
        f"{instance.menu.restaurant.pk}-{instance.menu.restaurant.slug}/"\
        f"menusection-{instance.pk}-{instance.slug}{extension}"


class MenuSection(models.Model):

    menu = models.ForeignKey('Menu', on_delete=models.CASCADE)
    name = models.CharField(max_length=128, default=None, blank=False)
    slug = models.SlugField(max_length=128)
    image = models.ImageField(
        help_text="An image or logo for this section (optional)",
        upload_to=menusection_upload_to, blank=True, null=True)
    note = models.CharField(
            help_text="An optional note about this section (e.g."
                      "'Drinks come with complimentary refills.')",
            max_length=256, blank=True, null=True)

    def __str__(self):
        return f"{self.menu.restaurant.name}: {self.menu.name} - {self.name}"

    def clean(self):
        # do not allow slugs to be reserved keywords
        if self.slug in constants.RESERVED_KEYWORDS:
            raise ValidationError(constants.RESERVED_KEYWORD_ERROR_STRING)

        # do not allow a menu to have duplicate section slugs
        menusections_with_same_slug = MenuSection.objects.filter(
            menu=self.menu,
            slug=slugify(self.name))
        if menusections_with_same_slug.count():
            if menusections_with_same_slug.first() != self \
                    or menusections_with_same_slug.last() != self:
                raise ValidationError(
                    "This name is too similar to one of this menu's "
                    "existing section names.")

    def get_absolute_url(self):
        return reverse('menus:menusection_detail', kwargs={
            'restaurant_slug': self.menu.restaurant.slug,
            'menu_slug': self.menu.slug,
            'menusection_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug == slugify(self.name):
            self.slug = slugify(self.name)
        self.clean()
        super().save(*args, **kwargs)


class MenuItem(models.Model):
    menusection = models.ForeignKey('MenuSection', on_delete=models.CASCADE)
    name = models.CharField(max_length=128, default=None, blank=False)
    slug = models.SlugField(max_length=128)
    price = models.IntegerField(
        help_text="Enter the price in cents (e.g. $5.00 = 500 cents)",
        blank=True, null=True)
    description = models.CharField(max_length=1024, blank=True)

    def __str__(self):
        return f"{self.menusection.menu.restaurant.name}: "\
            f"{self.menusection.menu.name} - {self.menusection.name} - "\
            f"{self.name}"

    def clean(self):
        # do not allow slugs to be reserved keywords
        if self.slug in constants.RESERVED_KEYWORDS:
            raise ValidationError(constants.RESERVED_KEYWORD_ERROR_STRING)

        # do not allow a menusection to have duplicate menuitem slugs
        menuitems_with_same_slug = MenuItem.objects.filter(
            menusection=self.menusection,
            slug=slugify(self.name))
        if menuitems_with_same_slug.count():
            if menuitems_with_same_slug.first() != self \
                    or menuitems_with_same_slug.last() != self:
                raise ValidationError(
                    "This name is too similar to one of this menu's "
                    "existing item names.")

    def get_absolute_url(self):
        return reverse('menus:menuitem_detail', kwargs={
            'restaurant_slug': self.menusection.menu.restaurant.slug,
            'menu_slug': self.menusection.menu.slug,
            'menusection_slug': self.menusection.slug,
            'menuitem_slug': self.slug})

    def get_readable_price(self):
        dollars = int(self.price / 100)
        cents = self.price - (dollars * 100)
        padded_cents = str(cents).zfill(2)
        return f"${dollars}.{padded_cents}"

    def save(self, *args, **kwargs):
        if not self.slug == slugify(self.name):
            self.slug = slugify(self.name)
        self.clean()
        super().save(*args, **kwargs)
