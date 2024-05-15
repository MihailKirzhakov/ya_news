import pytest

from http import HTTPStatus

from django.urls import reverse
from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_anonymous_user_cannot_send_comment(client, post):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', kwargs={'pk': post.pk})
    response = client.post(url, {'text': 'Текст комментария'})
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.exists()


@pytest.mark.django_db
def test_author_user_can_send_comment(author_client, post):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', kwargs={'pk': post.pk})
    response = author_client.post(url, {'text': 'Текст комментария'})
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.exists()


@pytest.mark.django_db
def test_edit_comment(author_client, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    response = author_client.post(url, {'text': 'New text'})
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == 'New text'


@pytest.mark.django_db
def test_edit_comment_not_author(not_author_client, comment):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_delete_comment(author_client, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()


@pytest.mark.django_db
def test_delete_comment_not_author(not_author_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_comment_with_bad_word(author_client, post):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_word = 'редиска'
    comment_text = f'Test comment with {bad_word}'
    data = {'text': comment_text}
    response = author_client.post(reverse('news:detail', args=[post.pk]), data)
    assert response.status_code == 200
    assert 'form' in response.context_data
    form = response.context_data['form']
    assert not form.is_valid()
    assert form.errors['text'][0] == WARNING
