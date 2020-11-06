import factory

from restaurants.models import Restaurant

class RestaurantFactory(factory.Factory):
    class Meta:
        model = Restaurant
        
    name = factory.Sequence(lambda n: f'Test Restaurant {n+1}')

class RandomRestaurantFactory(factory.Factory):
    class Meta:
        model = Restaurant

    name = factory.Faker('company')
