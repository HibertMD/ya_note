from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )

    def test_anonymous_pages_availability(self):
        urls = ('notes:home', 'users:login', 'users:logout', 'users:signup')
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authenticated_pages_availability(self):
        urls = ('notes:list', 'notes:success', 'notes:add')
        self.client.force_login(self.reader)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in (
                    'notes:delete',
                    'notes:edit',
                    'notes:detail',
            ):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls =  (
                ('notes:list', None),
                ('notes:success', None),
                ('notes:add', None),
                ('notes:detail', self.note.slug),
                ('notes:edit', self.note.slug),
                ('notes:delete', self.note.slug),
        )
        for name, args in urls:
            with self.subTest(name=name):
                if args is not None:
                    url = reverse(name, args=(args,))
                else:
                    url = reverse(name)
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(response, redirect_url)
