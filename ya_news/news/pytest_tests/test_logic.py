import pytest

from http import HTTPStatus

from django.shortcuts import get_object_or_404
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(get_url_news_detail,
                                            client, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    comments_before = Comment.objects.count()
    response = client.post(get_url_news_detail, data=form_data)
    comments_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.FOUND
    assert comments_before == comments_after


def test_user_can_create_comment(not_author_client,
                                 get_url_news_detail,
                                 form_data):
    """Авторизованный пользователь может отправить комментарий."""
    comments_before = Comment.objects.count()
    response = not_author_client.post(get_url_news_detail, data=form_data)
    assertRedirects(response, f'{get_url_news_detail}#comments')
    comments_after = Comment.objects.count()
    assert comments_after == comments_before + 1


def test_user_cant_use_bad_words(get_url_news_detail,
                                 not_author_client,
                                 bad_words_fixture):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    response = not_author_client.post(get_url_news_detail,
                                      data=bad_words_fixture)
    comments_count = Comment.objects.count()
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert comments_count == 0


def test_author_can_delete_comment(
        author_client, get_url_comment_delete, get_url_news_detail
):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_before = Comment.objects.count()
    response = author_client.delete(get_url_comment_delete)
    comments_after = Comment.objects.count()
    assertRedirects(response, f'{get_url_news_detail}#comments')
    assert comments_after == comments_before - 1


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
        get_url_comment_delete, admin_client,
):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comments_before = Comment.objects.count()
    response = admin_client.delete(get_url_comment_delete)
    comments_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_after == comments_before


def test_author_can_edit_comment(
        author_client, comment, get_url_comment_edit,
        get_url_news_detail, form_data
):
    """
    Авторизованный пользователь может редактировать
    свои комментарии.
    """
    response = author_client.post(get_url_comment_edit, data=form_data)
    assertRedirects(response, f'{get_url_news_detail}#comments')
    comment = get_object_or_404(Comment, pk=comment.pk)
    assert comment.text == 'Новый'


def test_user_cant_edit_comment_of_another_user(
        get_url_comment_edit, comment, not_author_client, form_data
):
    """
    Авторизованный пользователь не может редактировать
    чужие комментарии.
    """
    response = not_author_client.post(get_url_comment_edit, data=form_data)
    comment = get_object_or_404(Comment, pk=comment.pk)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment.text == 'Текст комментария'
