from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from menus_project import constants


class Restaurant(models.Model):
    name = models.CharField(max_length=128, default=None, blank=False)
    slug = models.SlugField(max_length=128, unique=True)
    admin_users = models.ManyToManyField(settings.AUTH_USER_MODEL)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        # do not allow slugs to be reserved keywords
        if self.slug in constants.RESERVED_KEYWORDS:
            raise ValidationError(constants.RESERVED_KEYWORD_ERROR_STRING)

        # do not allow duplicate restaurant slugs
        restaurants_with_same_slug = \
            Restaurant.objects.filter(slug=slugify(self.name))
        if restaurants_with_same_slug.exists() \
            and restaurants_with_same_slug.first() != self \
                and restaurants_with_same_slug.last() != self:
            raise ValidationError(
                constants.RESTAURANT_DUPLICATE_SLUG_ERROR_STRING)

    def get_absolute_url(self):
        return reverse('restaurants:restaurant_detail', kwargs={
            'restaurant_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug == slugify(self.name):
            self.slug = slugify(self.name)
        self.clean()
        super().save(*args, **kwargs)
