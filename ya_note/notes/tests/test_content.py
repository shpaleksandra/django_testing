from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note, User


class TestDetailNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.user = User.objects.create(username='Username')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='slug',
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.add_url = reverse('notes:add')
        cls.list_url = reverse('notes:list')

    def test_note_on_list_of_notes(self):
        """
        Отдельная заметка передаётся на страницу
        со списком заметок в списке
        object_list в словаре context
        """
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertEqual(object_list[0], self.note)

    def test_note_not_in_list_for_another_user(self):
        """
        В список заметок одного пользователя
        не попадают заметки другого пользователя
        """
        url = reverse('notes:list')
        response = self.user_client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_add_and_edit_forms(self):
        """
        На страницы создания и редактирования
        заметки передаются формы
        """
        for name, args in (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None),
        ):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
