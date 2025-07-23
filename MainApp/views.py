from idlelib.iomenu import errors
from django.db.models import Q
from MainApp.models import Snippet
from django.http import Http404, HttpResponseForbidden
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from MainApp.forms import SnippetForm
from MainApp.models import LANG_ICONS
from django.contrib import auth
from django.contrib.auth.decorators import login_required


def get_icon(lang):
    return LANG_ICONS.get(lang)


def index_page(request):
    context = {
        'pagename': 'Главное меню'
    }
    return render(request, 'pages/index.html', context)


@login_required
def snippet_create(request):
    if request.method == 'GET':
        form = SnippetForm()
        context = {
            "pagename": "Создание сниппета",
            'form': form
        }
        return render(request, 'pages/snippet_add_or_edit.html', context)

    if request.method == "POST":
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.user = request.user
            snippet.save()
            return redirect("snippets-list")

        else:
            context = {
                "form": form,
                "pagename": "Создание сниппета"
            }
            return render(request, 'pages/snippet_add_or_edit.html', context)


def snippets_list(request):
    if request.user.is_authenticated:
        snippets = Snippet.objects.filter(
            Q(access="public") | Q(user=request.user)
        ).distinct()
    else:
        snippets = Snippet.objects.filter(access="public")

    for snippet in snippets:
        snippet.icon = get_icon(snippet.lang)
    context = {
        'pagename': "Список всех сниппетов",
        'snippets': snippets
    }
    return render(request, 'pages/snippets_all_list.html', context)


@login_required
def user_list(request):
    snippets = Snippet.objects.filter(user=request.user)
    for snippet in snippets:
        snippet.icon = get_icon(snippet.lang)
    context = {
        'pagename': "Мои сниппеты",
        'snippets': snippets
    }
    return render(request, 'pages/snippets_user_list.html', context)


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


@login_required
def snippet_delete(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    if snippet.user != request.user:
        context = {
            "snippet": snippet,
            "errors": ["У вас нету доступа на удаление"]
        }
        return render(request, 'pages/snippet_page.html', context)

    snippet.delete()
    return redirect("snippets-user-list")


@login_required
def snippet_edit(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    if snippet.user != request.user:
        context = {
            "snippet": snippet,
            "errors": ["У вас нету доступа на изменения"]
        }
        return render(request, 'pages/snippet_page.html', context)

    if request.method == 'GET':
        form = SnippetForm(instance=snippet)
        context = {
            'pagename': 'Редактирование cниппета',
            'form': form,
            'edit': True,
            'id': id
        }
        return render(request, 'pages/snippet_add_or_edit.html', context)

    if request.method == "POST":
        form = SnippetForm(request.POST, instance=snippet)
        if form.is_valid():
            form.save()
            return redirect("snippets-user-list")
        else:
            context = {
                'form': form,
                'pagename': 'Редактирование cниппета'
            }
            return render(request, 'pages/snippet_add_or_edit.html', context)


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

