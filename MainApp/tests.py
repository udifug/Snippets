import pytest
from django.test import TestCase
from MainApp.models import Snippet, Tag, Comment
from django.contrib.auth.models import User


# Create your tests here.
@pytest.mark.django_db
class TestSnippetModel:
    """Тест для Snippet"""

    def test_snippet_creation(self):
        snippet = Snippet.objects.create(
            name='test snippet',
            lang='java',
            code='1+1=3',
            access='public'
        )

        assert snippet.name == 'test snippet'
        assert snippet.lang == 'java'
        assert snippet.code == '1+1=3'
        assert snippet.access == 'public'

    def test_snippet_with_user(self):
        """создаем пользователя с спиппетом """
        user = User.objects.create(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        snippet = Snippet.objects.create(
            name="User Snippet",
            lang="javascript",
            code="console.log('Hello');",
            user=user,
            access='private'
        )
        assert snippet.user == user
        assert snippet.access == 'private'
        assert snippet.code == "console.log('Hello');"

    def test_snippet_views_count_increment(self):
        """ увеличение просмотров сниппета"""
        snippet = Snippet.objects.create(
            name="Views Test",
            lang="python",
            code="pass",
        )
        initial_views = snippet.views_count
        snippet.views_count += 1
        snippet.save()

        updated_snippet = Snippet.objects.get(id=snippet.id)
        assert updated_snippet.views_count == initial_views + 1


@pytest.mark.django_db
class TestSnippetRelationships:
    """Тесты связей между моделями"""

    def test_snippet_with_tags(self):
        snippet = Snippet.objects.create(
            name="Tagged Snippet",
            lang="python",
            code="pass"
        )
        tag1 = Tag.objects.create(name="Python")
        tag2 = Tag.objects.create(name="Beginner")

        snippet.tags.add(tag1, tag2)
        assert snippet.tags.count() == 2
        assert tag1 in snippet.tags.all()
        assert tag2 in snippet.tags.all()

    def test_snippet_comments_relationship(self):
        """Тест связи сниппета с комментариями"""
        user1 = User.objects.create_user(username="user1", password="pass123")
        user2 = User.objects.create_user(username="user2", password="pass123")

        snippet = Snippet.objects.create(
            name="Commented Snippet",
            lang="python",
            code="pass"
        )

        comment1 = Comment.objects.create(
            text="First comment",
            author=user1,
            snippet=snippet
        )

        comment2 = Comment.objects.create(
            text="Second comment",
            author=user2,
            snippet=snippet
        )
        assert snippet.comments.count() == 2
        assert comment1 in snippet.comments.all()
        assert comment2 in snippet.comments.all()


@pytest.mark.django_db
class TestTagModel:
    """Тесты для модели Tag"""

    def test_tag_creation(self):
        """Тест создания тега"""
        tag = Tag.objects.create(name='Python')
        assert tag.name == "Python"

    def test_duplicate_tag_names_not_allowed(self):
        """Тест, что теги с одинаковыми именами недопустимы"""
        from django.db import IntegrityError, transaction

        tag1 = Tag.objects.create(name="Python")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Tag.objects.create(name="Python")

            # Проверяем, что в базе данных остался только один тег с именем "Python"
        assert Tag.objects.filter(name="Python").count() == 1
        assert Tag.objects.get(name="Python") == tag1


@pytest.mark.django_db
class TestCommentModel:
    """Тесты для модели Comment"""


    def test_comment_creation(self):
        """Тест создания комментария"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        snippet = Snippet.objects.create(
            name="User Snippet",
            lang="javascript",
            code="console.log('Hello');",
            user=user,
            access='private'
        )
        comment = Comment.objects.create(
            text="comment",
            author=user,
            snippet=snippet)

        assert comment.author == user
        assert comment.snippet == snippet
        assert comment.text == "comment"