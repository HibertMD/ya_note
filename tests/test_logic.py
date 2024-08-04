from http import HTTPStatus

from django.core.exceptions import ValidationError
from django.test import Client, TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()

class TestNoteCreation(TestCase):

    LOGIN_URL = reverse('users:login')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.create_url = reverse('notes:add')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new_slug',
            'author': cls.author,
        }

    def test_user_can_create(self):
        response = self.auth_client.post(self.create_url, data=self.form_data)
        redirect_url = reverse('notes:success')
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 2)

    def test_anonymous_user_cant_create(self):
        response = self.client.post(self.create_url, data=self.form_data)
        redirect_url = f'{self.LOGIN_URL}?next={self.create_url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        response = self.auth_client.post(self.create_url, data=self.form_data)
        print(response)
        self.assertFormError(response, 'form', 'slug', errors=(
                    self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)


# class TestNoteEditDelete(TestCase):
#
#     LOGIN_URL = reverse('users:login')
#     NOTE_TEXT = 'текст'
#     NOTE_TITLE = 'заголовок'
#     NOTE_SLUG = 'slug'
#     NOTE_NEW_TEXT = 'новый текст'
#     NOTE_NEW_TITLE = 'новый заголовок'
#     NOTE_NEW_SLUG = 'new_slug'
#
#     @classmethod
#     def setUpTestData(cls):
#         cls.author = User.objects.create(username='Лев Толстой')
#         cls.reader = User.objects.create(username='Читатель простой')
#         cls.author_client = Client()
#         cls.author_client.force_login(cls.author)
#         cls.reader_client = Client()
#         cls.reader_client.force_login(cls.reader)
#         cls.note = Note.objects.create(
#             title=cls.NOTE_TITLE,
#             text=cls.NOTE_TEXT,
#             slug=cls.NOTE_SLUG,
#             author=cls.author,
#         )
#         cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
#         cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
#         cls.form_data = {
#             'title': cls.NOTE_NEW_TITLE,
#             'text': cls.NOTE_NEW_TEXT,
#             'slug': cls.NOTE_NEW_SLUG
#         }
#
#     def test_user_can_edit_note(self):
#         response = self.author_client.post(self.edit_url, data=self.form_data)
#         redirect_url = reverse('notes:success')
#         self.assertRedirects(response, redirect_url)
#         self.note.refresh_from_db()
#         self.assertEqual(self.note.title, self.NOTE_NEW_TITLE)
#         self.assertEqual(self.note.text, self.NOTE_NEW_TEXT)
#         self.assertEqual(self.note.slug, self.NOTE_NEW_SLUG)
#
#     def test_another_user_cant_edit_note(self):
#         response = self.reader_client.post(self.edit_url, data=self.form_data)
#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
#         self.note.refresh_from_db()
#         self.assertEqual(self.note.title, self.NOTE_TITLE)
#         self.assertEqual(self.note.text, self.NOTE_TEXT)
#         self.assertEqual(self.note.slug, self.NOTE_SLUG)
#
#     def test_user_can_delete_note(self):
#         response = self.author_client.delete(self.delete_url)
#         redirect_url = reverse('notes:success')
#         self.assertRedirects(response, redirect_url)
#         notes_count = Note.objects.count()
#         self.assertEqual(notes_count, 0)
#
#     def test_another_user_cant_delete_note(self):
#         response = self.reader_client.delete(self.delete_url)
#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
#         notes_count = Note.objects.count()
#         self.assertEqual(notes_count, 1)
