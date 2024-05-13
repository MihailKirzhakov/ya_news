import pytest

from http import HTTPStatus

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', (
        'news:home', 'users:login', 'users:logout', 'users:signup'
    )
)
def test_anonymous_access_to_home_page(not_author_client, name):
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK
