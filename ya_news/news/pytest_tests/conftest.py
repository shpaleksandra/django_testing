import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse
from django.test.client import Client

from news.models import Comment, News
from news.forms import BAD_WORDS


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news


@pytest.fixture
def all_news_list():
    today = datetime.today()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        one_news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        )
        all_news.append(one_news)
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def get_url_news_home():
    return reverse('news:home')


@pytest.fixture
def get_url_news_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def get_url_comment_edit(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def get_url_comment_delete(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def bad_words_fixture():
    return {'text': f'Текст раз, {BAD_WORDS[0]}, и дальше'}


@pytest.fixture
def form_data():
    return {
        'text': 'Новый',
    }
