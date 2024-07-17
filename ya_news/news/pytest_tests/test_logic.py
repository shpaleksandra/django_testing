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
    comments_before = Comment.objects.count()
    response = client.post(get_url_news_detail, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comments_after = Comment.objects.count()
    assert comments_before == comments_after


def test_user_can_create_comment(not_author_client,
                                 get_url_news_detail,
                                 form_data):
    comments_before = Comment.objects.count()
    response = not_author_client.post(get_url_news_detail, data=form_data)
    assertRedirects(response, f'{get_url_news_detail}#comments')
    comments_after = Comment.objects.count()
    assert comments_after == comments_before + 1


def test_user_cant_use_bad_words(get_url_news_detail,
                                 not_author_client,
                                 bad_words_fixture):
    response = not_author_client.post(get_url_news_detail,
                                      data=bad_words_fixture)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(
        author_client, get_url_comment_delete, get_url_news_detail
):
    comments_before = Comment.objects.count()
    response = author_client.delete(get_url_comment_delete)
    assertRedirects(response, f'{get_url_news_detail}#comments')
    comments_after = Comment.objects.count()
    assert comments_after == comments_before - 1


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
        get_url_comment_delete, admin_client,
):
    comments_before = Comment.objects.count()
    response = admin_client.delete(get_url_comment_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_after = Comment.objects.count()
    assert comments_after == comments_before


def test_author_can_edit_comment(
        author_client, comment, get_url_comment_edit,
        get_url_news_detail, form_data
):
    response = author_client.post(get_url_comment_edit, data=form_data)
    assertRedirects(response, f'{get_url_news_detail}#comments')
    comment = get_object_or_404(Comment, pk=comment.pk)
    assert comment.text == 'Новый'


def test_user_cant_edit_comment_of_another_user(
        get_url_comment_edit, comment, not_author_client, form_data
):
    response = not_author_client.post(get_url_comment_edit, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment = get_object_or_404(Comment, pk=comment.pk)
    assert comment.text == 'Текст комментария'
