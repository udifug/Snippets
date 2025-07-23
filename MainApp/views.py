from idlelib.iomenu import errors

from MainApp.models import Snippet
from django.http import Http404
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from MainApp.forms import SnippetForm
from MainApp.models import LANG_ICONS
from django.contrib import auth


def get_icon(lang):
    return LANG_ICONS.get(lang)
def index_page(request):
    context = {
        'pagename': 'Главное меню'
    }
    return render(request, 'pages/index.html', context)


def snippet_create(request):
    if request.method == 'GET':
        form = SnippetForm()
        context = {
            "pagename": "Создание сниппета",
            'form': form
        }
        return render(request, 'pages/add_snippet.html', context)

    if request.method == "POST":
        form = SnippetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("snippets-list")

        else:
            context = {
                "form": form,
                "pagename": "Создание сниппета"
            }
            return render(request, 'pages/add_snippet.html', context)


def snippets_list(request):
    snippets = Snippet.objects.all()
    for snippet in snippets:
        snippet.icon = get_icon(snippet.lang)
    context = {
        'pagename': "Список всех сниппетов",
        'snippets': snippets
    }
    return render(request, 'pages/view_snippets.html', context)


def snippet_page(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    snippet.views_count = F("views_count") + 1
    snippet.save(update_fields=['views_count'])
    snippet.refresh_from_db()
    context = {
        'pagename': "Информация о сниппете",
        'snippet': snippet
    }
    return render(request, 'pages/snippet_page.html', context)


def snippet_delete(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    snippet.delete()
    return redirect("snippets-list")


def snippet_edit(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    if request.method == 'GET':
        form = SnippetForm(instance=snippet)
        context = {
            'pagename': 'Редактирование cниппета',
            'form': form,
            'edit': True,
            'id': id
        }
        return render(request, 'pages/add_snippet.html', context)

    if request.method == "POST":
        form = SnippetForm(request.POST, instance=snippet)
        if form.is_valid():
            form.save()
            return redirect("snippets-list")

        else:
            context = {
                'form': form,
                'pagename': 'Редактирование cниппета'
            }
            return render(request, 'pages/add_snippet.html', context)

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(request, username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            context = {
                'errors': ['Некорректный логин или пароль'],
            }
            return render(request, 'pages/index.html', context)

def user_logout(request):
    auth.logout(request)
    return redirect('home')