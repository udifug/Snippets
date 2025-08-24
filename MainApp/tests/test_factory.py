import pytest
from IPython.core.release import authors

from MainApp.factories import UserFactory, SnippetFactory, TagFactory, CommentFactory
from MainApp.models import User, Tag, Snippet


@pytest.mark.django_db
def test_task1():
    UserFactory(username='Alice')
    user = User.objects.get(id=1)

    assert user.username == 'Alice'


@pytest.mark.django_db
def test_task2():
    TagFactory.create_batch(5)

    assert Tag.objects.count() == 5


@pytest.mark.django_db
def test_task3():
    SnippetFactory(name='Java Quick Sort', lang='java')
    snippet = Snippet.objects.get(id=1)

    assert snippet.name == 'Java Quick Sort'
    assert snippet.lang == 'java'


@pytest.mark.django_db
def test_task4():
    tag1 = TagFactory(name="web")
    tag2 = TagFactory(name="backend")

    snippet = SnippetFactory(access='public')
    snippet.tags.clear()
    snippet.tags.add(tag1, tag2)

    tag_names = list(snippet.tags.values_list("name", flat=True))
    assert 'web' in tag_names
    assert "backend" in tag_names
    assert len(tag_names) == 2


@pytest.mark.django_db
def test_task5():
    user = UserFactory(username='Commenter')
    snippet = SnippetFactory(name="My First Snippet")
    comment = CommentFactory(author=user, snippet=snippet)

    assert comment.author == user
    assert comment.snippet == snippet


@pytest.mark.django_db
def test_task6():
    snippets = SnippetFactory.create_batch(3, access='private')

    assert len(snippets) == 3
    for snippet in snippets:
        assert snippet.access == 'private'


@pytest.mark.django_db
def test_task7():
    user1 = UserFactory()
    user2 = UserFactory()

    snippet = SnippetFactory()

    comment1 = CommentFactory(author=user1, snippet=snippet)
    comment2 = CommentFactory(author=user2, snippet=snippet)

    assert comment1.author == user1
    assert comment2.author == user2
    assert comment1.snippet == snippet
    assert comment2.snippet == snippet
    assert snippet.comments.all().count() == 2


@pytest.mark.django_db
def test_task8():
    user1 = UserFactory()
    user2 = UserFactory()
    authors = [user1, user2]

    snippets = SnippetFactory.create_batch(10)

    for snippet in snippets:
        for i in range(10):
            author = authors[i % 2]
            CommentFactory(author=author, snippet=snippet)

        assert snippet.comments.count() == 10
