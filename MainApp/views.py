from MainApp.models import Snippet
from django.http import Http404
from django.shortcuts import render, redirect


def index_page(request):
    context = {
        'pagename': 'Главное меню'
    }
    return render(request, 'pages/index.html', context)


def add_snippet_page(request):
    context = {
        'pagename': 'Добавление нового сниппета'
    }
    return render(request, 'pages/add_snippet.html', context)


def snippets_page(request):
    snippets = Snippet.objects.all()
    context = {
        'pagename': "Список всех сниппетов",
        'snippets': snippets
    }
    return render(request, 'pages/view_snippets.html', context)


def view_snippet(request, id):
    snippet = Snippet.objects.get(id=id)
    context = {
        'pagename': "Информация о сниппете",
        'snippet': snippet
    }
    return render(request, 'pages/snippet_page.html', context)
