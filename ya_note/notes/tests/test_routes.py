from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse

from models import Note, User

class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='Категория',
        )

    def test_pages_availability(self):
        for name in (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        ):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
