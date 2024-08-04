from django.test import TestCase, Client

from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):

    NOTES_LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )

    def test_user_note_list(self):
        response = self.author_client.get(self.NOTES_LIST_URL)
        self.assertEqual(response.context['object_list'].count(), 1)

    def test_another_user_note_list(self):
        response = self.reader_client.get(self.NOTES_LIST_URL)
        self.assertEqual(response.context['object_list'].count(), 0)

    def test_user_note_create_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', self.note.slug),
        )
        for name, args in urls:
            with self.subTest(name=name):
                if args is not None:
                    url = reverse(name, args=(args,))
                else:
                    url = reverse(name)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
