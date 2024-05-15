import pytest
from http import HTTPStatus
from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import reverse
from news.models import News, Comment


class TestNewsListView(TestCase):
    def setUp(self):
        self.news1 = News.objects.create(
            title='Новость 1', text='Текст 1', date=datetime.today()
        )
        self.news2 = News.objects.create(
            title='Новость 2', text='Текст 2',
            date=datetime.today() - timedelta(days=1)
        )
        self.news3 = News.objects.create(
            title='Новость 3', text='Текст 3',
            date=datetime.today() - timedelta(days=2)
        )

    def test_news_list_sorted(self):
        """
        Новости отсортированы от самой свежей к самой старой.
        Свежие новости в начале списка.
        """
        response = self.client.get(reverse('news:home'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        news_list = response.context['object_list']
        self.assertEqual(
            [news.pk for news in news_list],
            [self.news1.pk, self.news2.pk, self.news3.pk]
        )


@pytest.mark.django_db
def test_comments_sorted_chronologically(author, author_client, post, comment):
    """
    Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.
    """
    new_comment = Comment.objects.create(
        news=post,
        author=author,
        text='Еще один комментарий',
    )
    new_comment.created = comment.created + timedelta(minutes=1)
    new_comment.save()
    response = author_client.get(
        reverse('news:detail', kwargs={'pk': post.pk})
    )
    assert list(
        response.context['object'].comment_set.all()
    ) == [comment, new_comment]


@pytest.mark.django_db
def test_news_count_on_home_page(not_author_client):
    """Количество новостей на главной странице — не более 10."""
    response = not_author_client.get(reverse('news:home'))
    assert len(response.context['object_list']) <= 10


@pytest.mark.django_db
def test_anonymous_user_cannot_access_comment_form(client, post):
    """
    Анонимному пользователю недоступна форма
    для отправки комментария на странице отдельной новости
    """
    url = reverse('news:detail', kwargs={'pk': post.pk})
    response = client.get(url)
    assert 'form' not in response.context
    assert response.status_code == HTTPStatus.OK


def test_author_user_can_comment_on_detail_page(author_client, post):
    """
    Авторизованному пользователю доступна форма
    для отправки комментария на странице отдельной новости
    """
    response = author_client.get(reverse('news:detail', args=[post.pk]))
    assert 'form' in response.context
