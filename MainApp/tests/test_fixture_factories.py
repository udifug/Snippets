import pytest
from MainApp.factories import TagFactory, UserFactory, CommentFactory, SnippetFactory
from MainApp.models import Tag, Snippet, Comment


@pytest.fixture
def tag_factory():
    def _create_tags(names):
        tags = []
        for name in names:
            tags.append(TagFactory(name=name))
        return tags

    return _create_tags


@pytest.fixture
def comment_factory():
    def _create_comment(snippet, n):
        return CommentFactory.create_batch(n, snippet=snippet)

    return _create_comment


@pytest.mark.django_db
def test_factory_tags(tag_factory):
    tags = tag_factory(names=["js", "basic", "oop"])

    assert Tag.objects.count() == 3

    assert tags[0].name == "js"
    assert tags[1].name == "basic"
    assert tags[2].name == "oop"


@pytest.mark.django_db
def test_factory_comment(comment_factory):
    snippet = SnippetFactory()
    comment_factory(snippet=snippet, n=6)

    comments = Comment.objects.all()
    assert Comment.objects.count() == 6

    for comment in comments:
        assert comment.snippet == snippet
