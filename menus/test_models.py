from django.test import TestCase

from menus.models import Menu

class MenuModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Menu.objects.create(
                name="Test Menu",
                )

    def test_name_label(self):
        menu = Menu.objects.first()
        field_label = menu._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        menu = Menu.objects.first()
        max_length = menu._meta.get_field('name').max_length
        self.assertEqual(max_length, 255)

    def test_object_string_representation_returns_name(self):
        menu = Menu.objects.first()
        expected_object_string = "Test Menu"
        self.assertEqual(str(menu), expected_object_string)

