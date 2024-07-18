import pytest
from django.conf import settings

pytestmark = pytest.mark.django_db


def test_news_count(all_news_list, get_url_news_home, client):
    """
    Количество новостей на главной странице —
    не более 10.
    """
    response = client.get(get_url_news_home)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(all_news_list, get_url_news_home, client):
    """
    Новости отсортированы от самой свежей к самой старой
    """
    response = client.get(get_url_news_home)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(all_news_list, get_url_news_detail, client):
    """
    Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке
    """
    response = client.get(get_url_news_detail)
    news = response.context['news']
    comments = news.comment_set.all()
    dates = [comment.created for comment in comments]
    dates_sorted = sorted(dates)
    assert 'news' in response.context
    assert dates == dates_sorted


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True),
    ),
)
def test_pages_contains_form(news, parametrized_client, expected_status,
                             get_url_news_detail):
    """
    Анонимному пользователю недоступна форма для отправки
    комментария на странице отдельной новости,
    а авторизованному доступна.
    """
    response = parametrized_client.get(get_url_news_detail)
    assert ('form' in response.context) is expected_status
