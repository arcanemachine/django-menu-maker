from django.forms import widgets
from django.test import SimpleTestCase

from menus.forms import *

class MenuSectionCreateFormTest(SimpleTestCase):

    def setUp(self):
        self.form = MenuSectionCreateForm

    def test_meta_model_name(self):
        self.assertEqual(self.form._meta.model.__name__, 'MenuSection')

    def test_meta_fields(self):
        self.assertEqual(self.form._meta.fields, ['menu', 'name'])

    def test_meta_widgets(self):
        self.assertTrue(isinstance(self.form._meta.widgets['menu'],
            widgets.HiddenInput))

class MenuItemFormTest(SimpleTestCase):

    def setUp(self):
        self.form = MenuItemForm

    def test_meta_model_name(self):
        self.assertEqual(self.form._meta.model.__name__, 'MenuItem')

    def test_meta_fields(self):
        self.assertEqual(self.form._meta.fields,
            ['menusection', 'name', 'description'])

    def test_meta_widgets(self):
        self.assertTrue(isinstance(self.form._meta.widgets['menusection'],
            widgets.HiddenInput))

