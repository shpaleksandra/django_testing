import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """
    Главная стрнаница, страницы регистрации, входа и выхода
    доступны для анонимного пользователя
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_detail_page_availability(get_url_news_detail, client):
    """
    Страница отдельной новости
    доступна для анонимного пользователя
    """
    response = client.get(get_url_news_detail)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'get_url',
    (
        pytest.lazy_fixture('get_url_comment_edit'),
        pytest.lazy_fixture('get_url_comment_delete'),
    ),
)
def test_edit_delete_comment_for_different_users(
        parametrized_client, get_url, expected_status
):
    """
    Страницы удаления и редактирования комментария
    доступны автору, а также авторизованный пользователь
    не может зайти на редактирование и удаление чужих
    комментариев
    """
    response = parametrized_client.get(get_url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'get_url',
    (
        pytest.lazy_fixture('get_url_comment_edit'),
        pytest.lazy_fixture('get_url_comment_delete'),
    ),
)
def redirect_to_login_from_comments(get_url, url_user_login, client):
    """
    Редирект анонимного пользователя при попытке
    редактирования или удаления комментария
    """
    expected_url = f'{url_user_login}?next={get_url}'
    response = client.get(get_url)
    assertRedirects(response, expected_url)
