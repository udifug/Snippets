import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from MainApp.models import Snippet, Comment
from MainApp.factories import UserFactory, SnippetFactory, CommentFactory


@pytest.fixture
def client():
    """Фикстура для создания тестового клиента"""
    return Client()


@pytest.fixture
def user():
    """Фикстура для создания пользователя"""
    return UserFactory()


@pytest.fixture
def authenticated_client(client, user):
    """Фикстура для создания аутентифицированного клиента"""
    client.force_login(user)
    return client, user


@pytest.fixture
def snippet(user):
    """Фикстура для создания сниппета"""
    return SnippetFactory(user=user)


@pytest.fixture
def comment_data(snippet):
    """Фикстура для данных комментария"""
    return {
        'text': 'Тестовый комментарий',
        'snippet_id': snippet.id
    }


@pytest.mark.django_db
class TestCommentAdd:
    """Тесты для функции comment_add"""

    def test_comment_add_success(self, authenticated_client, snippet, comment_data):
        """Тест успешного добавления комментария"""
        client, user = authenticated_client

        # Проверяем, что пользователь аутентифицирован
        assert user.is_authenticated

        # Отправляем POST запрос для добавления комментария
        response = client.post(reverse('comment-add'), comment_data)

        # Проверяем, что произошло перенаправление на страницу сниппета
        assert response.status_code == 302
        assert response.url == reverse('snippet-page', kwargs={'id': snippet.id})

        # Проверяем, что комментарий был создан в базе данных
        comment = Comment.objects.filter(snippet=snippet).first()
        assert comment is not None
        assert comment.text == comment_data['text']
        assert comment.author == user
        assert comment.snippet == snippet

    def test_comment_add_not_authenticated(self, client, snippet, comment_data):
        """Тест попытки добавления комментария неаутентифицированным пользователем"""
        # Отправляем POST запрос без аутентификации
        response = client.post(reverse('comment-add'), comment_data)

        # Проверяем, что произошло перенаправление на страницу входа
        assert response.status_code == 302
        assert '/login' in response.url

        # Проверяем, что комментарий не был создан
        comment_count = Comment.objects.filter(snippet=snippet).count()
        assert comment_count == 0

    def test_comment_add_invalid_snippet_id(self, authenticated_client, comment_data):
        """Тест добавления комментария к несуществующему сниппету"""
        client, user = authenticated_client

        # Устанавливаем несуществующий ID сниппета
        comment_data['snippet_id'] = 99999

        # Отправляем POST запрос
        response = client.post(reverse('comment-add'), comment_data)

        # Проверяем, что получили 404 ошибку
        assert response.status_code == 404

        # Проверяем, что комментарий не был создан
        comment_count = Comment.objects.count()
        assert comment_count == 0

    def test_comment_add_invalid_form_data(self, authenticated_client, snippet):
        """Тест добавления комментария с невалидными данными формы"""
        client, user = authenticated_client

        # Отправляем пустой текст комментария
        invalid_data = {
            'text': '',  # Пустой текст
            'snippet_id': snippet.id
        }

        # Отправляем POST запрос
        response = client.post(reverse('comment-add'), invalid_data)

        # Проверяем, что произошло перенаправление (форма невалидна, но сниппет существует)
        assert response.status_code == 302
        assert response.url == reverse('snippet-page', kwargs={'id': snippet.id})

        # Проверяем, что комментарий не был создан из-за невалидности формы
        comment_count = Comment.objects.filter(snippet=snippet).count()
        assert comment_count == 0

    def test_comment_add_get_request(self, authenticated_client):
        """Тест GET запроса к comment_add (должен вернуть 404)"""
        client, user = authenticated_client
        response = client.get(reverse('comment-add'))

        # Проверяем, что получили 404 ошибку
        assert response.status_code == 404

    def test_comment_add_multiple_comments(self, authenticated_client, snippet):
        """Тест добавления нескольких комментариев к одному сниппету"""
        client, user = authenticated_client

        comments_data = [
            {'text': 'Первый комментарий', 'snippet_id': snippet.id},
            {'text': 'Второй комментарий', 'snippet_id': snippet.id},
            {'text': 'Третий комментарий', 'snippet_id': snippet.id}
        ]

        # Добавляем несколько комментариев
        for comment_data in comments_data:
            response = client.post(reverse('comment-add'), comment_data)
            assert response.status_code == 302

        # Проверяем, что все комментарии были созданы
        comments = Comment.objects.filter(snippet=snippet)
        assert comments.count() == 3

        # Проверяем содержимое комментариев
        comment_texts = [comment.text for comment in comments]
        expected_texts = ['Первый комментарий', 'Второй комментарий', 'Третий комментарий']
        assert sorted(comment_texts) == sorted(expected_texts)

    def test_comment_add_different_users(self, client, snippet):
        """Тест добавления комментариев разными пользователями"""
        users = UserFactory.create_batch(3)

        comments_data = [
            {'text': f'Комментарий от {user.username}', 'snippet_id': snippet.id}
            for user in users
        ]

        # Каждый пользователь добавляет свой комментарий
        for user, comment_data in zip(users, comments_data):
            client.force_login(user)
            response = client.post(reverse('comment-add'), comment_data)
            assert response.status_code == 302

        # Проверяем, что все комментарии были созданы с правильными авторами
        comments = Comment.objects.filter(snippet=snippet)
        assert comments.count() == 3

        for comment in comments:
            assert comment.author in users


    def test_comment_add_missing_snippet_id(self, authenticated_client):
        """Тест добавления комментария без указания snippet_id"""
        client, user = authenticated_client
        # Отправляем POST запрос, не указав snippet_id
        comment_data = {
            'text': "Hello",
        }
        response = client.post(reverse('comment-add'),comment_data)
        # Проверяем, что получили 404 ошибку
        assert response.status_code == 404

        # Проверяем, что комментарий не был создан
        assert Comment.objects.count() == 0

    def test_comment_add_long_text(self, authenticated_client, snippet):
        """Тест добавления комментария с длинным текстом"""
        client, user = authenticated_client

        long_text = 'Очень длинный комментарий .' * 100  # Создаем длинный текст 2600
        comment_data = {
            'text': long_text,
            'snippet_id': snippet.id
        }

        response = client.post(reverse('comment-add'), comment_data)

        # Проверяем, что комментарий был успешно добавлен
        assert response.status_code == 302
        assert response.url == reverse('snippet-page', kwargs={'id': snippet.id})

        # Проверяем, что комментарий был создан с полным текстом
        comment = Comment.objects.filter(snippet=snippet).first()
        assert comment is not None
        assert len(comment.text) == len(long_text)