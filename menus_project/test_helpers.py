from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse

from menus_project.helpers import get_next_url


class GetNextUrlTest(SimpleTestCase):

    def setUp(self):
        self.url = reverse('users:login')
        self.next_url = reverse('users:user_detail')

    def test_with_next_karg(self):
        self.request = \
            RequestFactory().get(self.url + '?next=' + self.next_url)
        func_to_test = get_next_url(self.request, self.url)
        self.assertEqual(func_to_test, self.request.GET['next'])

    def test_without_next_kwarg(self):
        self.request = RequestFactory().get(self.url)
        func_to_test = get_next_url(self.request, self.url)
        self.assertEqual(func_to_test, self.url)
