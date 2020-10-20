from django.db import models

class Menu(models.Model):

    # restaurant = models.ForeignKey('restaurants.Restaurant')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
