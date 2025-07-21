from MainApp.models import Snippet
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from MainApp.forms import SnippetForm


def index_page(request):
    context = {
        'pagename': 'Главное меню'
    }
    return render(request, 'pages/index.html', context)

def snippet_create(request):
    if request.method == 'GET':
        form = SnippetForm()
        context = {
            'pagename': 'Добавление нового сниппета',
            'form': form
        }
        return render(request, 'pages/add_snippet.html', context)

    if request.method == "POST":
        form = SnippetForm(request.POST)
        if form.is_valid():
            form.save()
            # name = form.cleaned_data['name']
            # lang = form.cleaned_data['lang']
            # code = form.cleaned_data['code']
            #
            # Snippet.objects.create(name=name, lang=lang, code=code)
            return redirect("snippets-list")

        else:
            return render(request, 'pages/add_snippet.html', {"form":form})

def snippets_page(request):
    snippets = Snippet.objects.all()
    context = {
        'pagename': "Список всех сниппетов",
        'snippets': snippets
    }
    return render(request, 'pages/view_snippets.html', context)

def snippet_page(request, id):
    snippet = get_object_or_404(Snippet, id=id)
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
            'pagename': 'Редактировать сниппет',
            'form': form,
            'edit':True,
            'id': id
        }
        return render(request, 'pages/add_snippet.html', context)

    if request.method == "POST":
        form = SnippetForm(request.POST,instance=snippet)
        if form.is_valid():
            form.save()
            return redirect("snippets-list")