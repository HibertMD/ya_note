from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()
NOTES_QUANTITY = 10

class TestListPage(TestCase):

    NOTES_LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        all_notes = [
            Note(
                title=f'Заголовок{index}',
                text=f'Текст{index}',
                slug=f'slug_{index}',
                author=cls.author,
            )
            for index in range(NOTES_QUANTITY)
        ]
        Note.objects.bulk_create(all_notes)

    def test_user_note_list(self):
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_LIST_URL)
        self.assertEqual(
            response.context['object_list'].count(),
            NOTES_QUANTITY
        )

    def test_another_user_note_list(self):
        response = self.client.get(self.NOTES_LIST_URL)
        self.client.force_login(self.reader)
        self.assertIsNone(response.context)


class TestDetailPage(TestCase):

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
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.creat_url = reverse('notes:add')

    def test_user_note_create_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.creat_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_user_note_detail(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIsNotNone(response.context)

    def test_another_user_note_detail(self):
        response = self.client.get(self.detail_url)
        self.assertIsNone(response.context)
