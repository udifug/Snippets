from idlelib.iomenu import errors
from MainApp.models import Snippet, Comment
from django.http import Http404, HttpResponse
from django.db.models import F, Q, Count, Avg
from django.shortcuts import render, redirect, get_object_or_404
from MainApp.forms import SnippetForm, UserRegistrationForm, CommentForm
from MainApp.models import LANG_ICONS, LANG_CHOICES, ACCESS_CHOICES
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User


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


def snippets_list(request, snippet_my):
    if snippet_my:
        if not request.user.is_authenticated:
            return HttpResponse('Unauthorized', status=401)
        snippets = Snippet.objects.filter(user=request.user)
        pagename = 'Мои сниппеты'

    else:
        if request.user.is_authenticated:
            snippets = Snippet.objects.filter(
                Q(access="public") | Q(user=request.user)
            )
        else:
            snippets = Snippet.objects.filter(access="public")
        pagename = "Список всех сниппетов"

    # filter
    lang = request.GET.get("lang")
    if lang:
        snippets = snippets.filter(lang=lang)
    user_id = request.GET.get("user_id")
    if user_id:
        snippets = snippets.filter(user__id=user_id)

    filtering = any([lang, user_id])

    # sort
    sort = request.GET.get("sort")
    if sort:
        snippets = snippets.order_by(sort)


    # paginator
    paginator = Paginator(snippets, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if filtering and not page_obj.object_list:
        empty_list = 'no_result'
    else:
        empty_list = 'no_data'

    users = User.objects.annotate(num_snippets=Count('snippet', filter=Q(snippet__access='public'))).filter(
        num_snippets__gt=0).order_by("-num_snippets")

    context = {
        'pagename': pagename,
        'page_obj': page_obj,
        'snippets': snippets,
        "sort": sort,
        "lang": lang,
        "user_id": user_id,
        "LANG_CHOICES": LANG_CHOICES,
        "users": users,
        'snippet_my': snippet_my,
        'empty_list': empty_list
    }
    return render(request, 'pages/snippets_list.html', context)

def snippets_stats(request):
    general_stats = Snippet.objects.aggregate(
        total_snippets = Count('id'),
        public_snippets = Count('id', filter=Q(access='public')),
        average_views = Avg('views_count'),

    )
    if general_stats['average_views'] is not None:
        general_stats['average_views'] = int(round(general_stats['average_views']))

    top_users = User.objects.annotate(num_snippets=Count('snippet')).order_by('-num_snippets')[:3]

    context ={
        "pagename": 'Статистика по сниппетам',
        'general_stats' : general_stats,
        'top_five' : Snippet.objects.order_by('-views_count')[:5],
        'top_users' : top_users

    }
    return render(request, 'pages/snippets_stats.html',context)

def snippet_detail(request, id):
    snippet = Snippet.objects.prefetch_related('comments').get(id=id)
    snippet.views_count = F("views_count") + 1
    snippet.save(update_fields=['views_count'])
    snippet.refresh_from_db()
    comments_form = CommentForm()
    comments = snippet.comments.all()

    context = {
        'snippet': snippet,
        'comments': comments,
        'comments_form': comments_form
    }
    return render(request, 'pages/snippet_detail.html', context)


@login_required
def comment_add(request):
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        snippet_id = request.POST.get("snippet_id")
        snippet = get_object_or_404(Snippet, id=snippet_id)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.snippet = snippet
            comment.save()
        return redirect("snippet-page", id=snippet_id)

    return Http404


@login_required
def snippet_delete(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    if snippet.user != request.user:
        context = {
            "snippet": snippet,
            "errors": ["У вас нету доступа на удаление"]
        }
        return render(request, 'pages/snippet_detail.html', context)

    snippet.delete()
    return redirect("snippets-mylist")


@login_required
def snippet_edit(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    if snippet.user != request.user:
        context = {
            "snippet": snippet,
            "errors": ["У вас нету доступа на изменения"]
        }
        return render(request, 'pages/snippet_detail.html', context)

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
            return redirect("snippets-mylist")
        else:
            context = {
                'form': form,
                'pagename': 'Редактирование cниппета'
            }
            return render(request, 'pages/snippet_add_or_edit.html', context)


def user_registration(request):
    if request.method == "GET":
        user_form = UserRegistrationForm()
        context = {
            "pagename": "Регистрация",
            'user_form': user_form
        }
        return render(request, 'pages/user_registration.html', context)

    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            messages.success(request, f'Добро пожаловать, {user.username}! Вы успешно зарегистрированы.')
            return redirect("home")
        else:
            context = {
                "pagename": "Регистрация",
                "user_form": user_form
            }
            return render(request, 'pages/user_registration.html', context)


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
                'pagename': 'Главное меню',
                'errors': ['Некорректный логин или пароль'],
            }
            return render(request, 'pages/index.html', context)


def user_logout(request):
    auth.logout(request)
    return redirect('home')
