import logging
import json
from idlelib.iomenu import errors
from MainApp.models import Snippet, Comment, Notification, LikeDislike
from django.http import Http404, HttpResponse, HttpResponseForbidden, JsonResponse
from django.db.models import F, Q, Count, Avg, Prefetch
from django.shortcuts import render, redirect, get_object_or_404
from MainApp.forms import SnippetForm, UserRegistrationForm, CommentForm, UserProfileForm, UserEditForm
from MainApp.models import LANG_ICONS, LANG_CHOICES, ACCESS_CHOICES
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from MainApp.signals import snippet_view, snippet_deleted
from MainApp.utils import send_activation_email, verify_activation_token

logger = logging.getLogger(__name__)


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
            messages.info(request, f"Сниппет был создан")
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

    # tags
    tag = request.GET.get('tag')
    if tag:
        snippets = snippets.filter(tags__name=tag)
        pagename = 'Сниппеты по выбранным тегам'

    snippets = snippets.select_related('user')
    # paginator
    paginator = Paginator(snippets, 10)
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
        "tag": tag,
        "user_id": user_id,
        "LANG_CHOICES": LANG_CHOICES,
        "users": users,
        'snippet_my': snippet_my,
        'empty_list': empty_list
    }
    return render(request, 'pages/snippets_list.html', context)


def snippets_stats(request):
    general_stats = Snippet.objects.aggregate(
        total_snippets=Count('id'),
        public_snippets=Count('id', filter=Q(access='public')),
        average_views=Avg('views_count'),
    )
    if general_stats['average_views'] is not None:
        general_stats['average_views'] = int(round(general_stats['average_views']))

    top_users = User.objects.annotate(num_snippets=Count('snippet')).order_by('-num_snippets')[:3]

    context = {
        "pagename": 'Статистика по сниппетам',
        'general_stats': general_stats,
        'top_five': Snippet.objects.order_by('-views_count')[:5],
        'top_users': top_users

    }
    return render(request, 'pages/snippets_stats.html', context)


def snippet_detail(request, id):
    snippet = Snippet.objects.prefetch_related("tags").get(id=id)

    if snippet.user != request.user and snippet.access == 'private':
        return HttpResponseForbidden('You are not authorized to access this page')

    snippet_view.send(sender=None, snippet=snippet)
    comments_form = CommentForm()

    sort = request.GET.get("sort")
    allow_sort = ['creation_date','-creation_date']
    if sort not in allow_sort:
        sort = '-creation_date'

    comments =  Comment.with_likes_count().select_related("author").filter(snippet=snippet).order_by(sort)

    paginator = Paginator(comments, 5)
    page_number = request.GET.get("page")
    page_comment = paginator.get_page(page_number)

    context = {
        'pagename': f'Сниппет: {snippet.name}',
        'snippet': snippet,
        'sort': sort,
        'page_obj': page_comment,
        'comments_form': comments_form,
        'all_comments' : comments.count()
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

        messages.info(request, f'Комментарий оставлен')
        return redirect("snippet-page", id=snippet_id)

    raise Http404


def comment_like(request):
    if request.method == "POST":
        data = json.loads(request.body)
        comment_id = data.get('comment_id')
        vote = data.get('vote')
        user = request.user

        comment = Comment.objects.get(id=comment_id)

        existing_vote = LikeDislike.objects.filter(
            user=user,
            content_type=ContentType.objects.get_for_model(Comment),
            object_id=comment_id,
        ).first()

        if existing_vote:
            if existing_vote.vote == vote:
                existing_vote.delete()
            else:
                existing_vote.vote = vote
                existing_vote.save()
        else:
            LikeDislike.objects.create(
                user=user,
                vote=vote,
                content_object=comment
            )

        updated = Comment.with_likes_count().get(id=comment.id)

        return JsonResponse({
            'status': 'ok',
            'like': updated.likes_count,
            'dislike': updated.dislikes_count
        })


@login_required
def snippet_delete(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    if snippet.user != request.user:
        context = {
            "snippet": snippet,
            "errors": ["У вас нету доступа на удаление"]
        }
        return render(request, 'pages/snippet_detail.html', context)

    snippet_id = snippet.id
    snippet.delete()

    snippet_deleted.send(sender=None, snippet_id=snippet_id)

    messages.info(request, 'Сниппет удален')
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
            messages.info(request, 'Сниппет изменен')
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
            send_activation_email(user, request)
            messages.success(request, f'Добро пожаловать, {user.username}! Проверьте свою почту и подтвердите email.')
            return redirect("home")
        else:
            context = {
                "pagename": "Регистрация",
                "user_form": user_form
            }
            return render(request, 'pages/user_registration.html', context)


def activate_account(request, user_id, token):
    """
    Подтверждение аккаунта пользователя по токену
    """
    try:
        user = User.objects.get(id=user_id)

        # Проверяем, не подтвержден ли уже аккаунт
        if user.is_active:
            messages.info(request, 'Ваш аккаунт уже подтвержден.')
            return redirect('home')

        # Проверяем токен
        if verify_activation_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request,
                             'Ваш аккаунт успешно подтвержден! Теперь вы можете войти в систему.')
            return redirect('home')
        else:
            messages.error(request,
                           'Недействительная ссылка для подтверждения. Возможно, она устарела.')
            return redirect('home')

    except User.DoesNotExist:
        messages.error(request, 'Пользователь не найден.')
        return redirect('home')

def user_profile(request):
    profile_stat = Snippet.objects.filter(user=request.user).aggregate(
        total_snippets=Count('id'),
        avg_views=Avg("views_count")
    )
    if profile_stat['avg_views'] is not None:
        profile_stat['avg_views'] = int(round(profile_stat['avg_views']))
    context = {
        "statistic": profile_stat,
        'top_five': Snippet.objects.order_by('-views_count')[:5]
    }
    return render(request, 'pages/user_profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль был изменен!')
            return redirect('user-profile')

    if request.method == 'GET':
        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }

    return render(request, 'pages/user_edit.html', context)


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


@login_required
def user_notifications(request):
    """Страница с уведомлениями пользователя"""
    # Отмечаем все уведомления как прочитанные при переходе на страницу

    # Получаем все уведомления для авторизованного пользователя, сортируем по дате создания
    notifications = Notification.objects.filter(recipient=request.user)

    notifications.update(is_read=True)

    context = {
        'pagename': 'Мои уведомления',
        'notifications': notifications
    }
    return render(request, 'pages/notifications.html', context)


def unread_notifications_count(request):
    """
    API endpoint для получения количества непрочитанных уведомлений
    Использует long polling - отвечает только если есть непрочитанные уведомления
    """
    from datetime import datetime
    import time

    # Максимальное время ожидания (30 секунд)
    max_wait_time = 30
    check_interval = 1  # Проверяем каждую секунду
    last_count = int(request.GET.get('last_count'))

    start_time = time.time()

    while time.time() - start_time < max_wait_time:
        # Получаем количество непрочитанных уведомлений
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

        # Если есть непрочитанные уведомления, сразу отвечаем
        if unread_count > last_count:
            return JsonResponse({
                'success': True,
                'unread_count': unread_count,
                'timestamp': str(datetime.now())
            })

        # Ждем перед следующей проверкой
        time.sleep(check_interval)

    # Если время истекло и нет уведомлений, возвращаем 0
    return JsonResponse({
        'success': True,
        'unread_count': 0,
        'timestamp': str(datetime.now())
    })


def notifications_delete(request):
    ...
