from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note, User


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Username')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.add_url = reverse('notes:add')
        cls.done_url = reverse('notes:success')
        cls.form_data = {'text': 'Текст',
                         'title': 'Заголовок',
                         'slug': 'slug',
                         'author': cls.user,
                         }

    def test_auth_user_can_create_note(self):
        response = self.auth_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note, Note.objects.get())
    
    def test_anonymous_cant_create_note(self):
        login_url = reverse('users:login')
        response = self.client.post(self.add_url, data=self.form_data)
        expected_url = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

# Невозможно создать две заметки с одинаковым slug.
    def test_authorized_user_cant_use_same_slug(self):
            self.note = Note.objects.create(
                title='Заголовок',
                text='Текст',
                author=self.user,
            )
            new_data = {
                'title': 'Новый заголовок',
                'text': 'Новый текст',
                'author': self.user,
                'slug': self.note.slug,
            }
            response = self.auth_client.post(self.add_url, data=new_data)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertFormError(
                response,
                form='form',
                field='slug',
                errors=(self.note.slug + WARNING),
            )
            notes_count = Note.objects.count()
            self.assertNotEqual(notes_count, 2)

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')
        response = self.auth_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(TestCase):
    TEXT = 'Старый текст'
    NEW_TEXT = 'Обновлённый текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Username')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='Пользователь')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Старый текст',
            author=cls.author,
            slug='slug',
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.done_url = reverse('notes:success')
        cls.form_data = {
            'text': cls.NEW_TEXT,
            'title': 'Заголовок',
            'author': cls.author,
            'slug': 'slug',
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.done_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        notes_count = Note.objects.count()
        response = self.user_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count, notes_count_after)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.user_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.TEXT)
