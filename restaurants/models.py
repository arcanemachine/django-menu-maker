from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Restaurant(models.Model):

    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128, unique=True, null=True)
    admin_users = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.name

    def clean(self):
        # do not allow duplicate restaurant slugs
        existing_restaurants_with_same_slug = \
            Restaurant.objects.filter(slug=slugify(self.name))
        if existing_restaurants_with_same_slug.exists():
            raise ValidationError("This restaurant name is already in use.")

    def get_absolute_url(self):
        return reverse('restaurants:restaurant_detail',
            kwargs={'restaurant_slug': self.slug })

    def save(self, *args, **kwargs):
        if not self.slug == slugify(self.name):
            self.slug = slugify(self.name)
        self.clean()
        super().save(*args, **kwargs)
