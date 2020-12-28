import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.timezone import now as timezone_now
from django.utils.text import slugify

from menus_project import constants


def upload_to(instance, filename):
    now = timezone_now()
    base, extension = os.path.splitext(filename)
    extension = extension.lower()
    return f"img/restaurants/{now:%Y/%m}/{instance.pk}{extension}"

class Restaurant(models.Model):
    name = models.CharField(max_length=128, default=None, blank=False)
    slug = models.SlugField(max_length=128, unique=True)
    admin_users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    image = models.ImageField(
        upload_to=upload_to, blank=True, null=True,
        help_text="An image or logo for your restaurant (optional)")

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

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete()
        super.delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('restaurants:restaurant_detail', kwargs={
            'restaurant_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug == slugify(self.name):
            self.slug = slugify(self.name)
        self.clean()
        super().save(*args, **kwargs)
