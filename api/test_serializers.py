from django.test import TestCase

from factories import RestaurantFactory
from .serializers import RestaurantSerializer

class RestaurantSerializerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.serializer = RestaurantSerializer
        cls.test_restaurant = RestaurantFactory.build_batch(3)

    def test_meta_model_name(self):
        self.assertEqual(self.serializer.Meta.model.__name__, 'Restaurant')

    def test_meta_model_fields(self):
        self.assertEqual(self.serializer.Meta.fields, ('id', 'name',))
