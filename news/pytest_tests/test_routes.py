import pytest

from http import HTTPStatus

from django.urls import reverse

from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', (
        'news:home', 'users:login', 'users:logout', 'users:signup'
    )
)
def test_anonymous_access_pages(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_anonymous_access_to_post_page(not_author_client, post):
    url = reverse('news:detail', kwargs={'pk': post.pk})
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name', (
        'news:edit', 'news:delete',
    )
)
def test_edit_delete_comment_availability(
    parametrized_client, name, comment, expected_status
):
    url = reverse(
        name, kwargs={'pk': comment.pk}
    )
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', (
        'news:edit', 'news:delete',
    )
)
def test_redirect_anonymous_to_login_page(
    client, name, comment
):
    login_url = reverse('users:login')
    url = reverse(
        name, kwargs={'pk': comment.pk}
    )
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
