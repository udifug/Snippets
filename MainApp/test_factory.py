import pytest
from MainApp.factories import UserFactory, SnippetFactory, TagFactory
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
    SnippetFactory(name='Java Quick Sort',lang='java')
    snippet = Snippet.objects.get(id=1)

    assert snippet.name == 'Java Quick Sort'
    assert snippet.lang == 'java'

@pytest.mark.django_db
def test_task4():
    tag1 = TagFactory(name= "web")
    tag2 = TagFactory(name="backend")
    SnippetFactory(access='public',tags=tag1)
    snippet = Snippet.objects.get(id=1)

    assert snippet.tags == 'web'

@pytest.mark.django_db
def test_task5():
    ...

@pytest.mark.django_db
def test_task6():
    ...

@pytest.mark.django_db
def test_task7():
    ...

@pytest.mark.django_db
def test_task8():
    ...