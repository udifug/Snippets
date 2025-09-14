from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, View, ListView, UpdateView
from MainApp.models import Snippet, Notification, LANG_CHOICES
from MainApp.forms import SnippetForm
from django.contrib import messages, auth
from django.shortcuts import  redirect
from django.db.models import Q, Count
from django.contrib.auth.models import User

class AddSnippetView(LoginRequiredMixin, CreateView):
    model = Snippet
    form_class = SnippetForm
    template_name = 'pages/snippet_add_or_edit.html'
    success_url = reverse_lazy('snippets-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = "Создание сниппета"
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f"Сниппет был создан")
        return super().form_valid(form)

class SnippetDetailView(DetailView):
    model = Snippet
    template_name = 'pages/snippet_detail.html'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        snippet = Snippet.objects.prefetch_related("tags").get(id=id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        snippet = self.get_object()
        context['pagename'] = f'Сниппет: {snippet.name}'
        return context

class UserLogoutView(View):
    def get(self, request):
        auth.logout(request)
        return redirect('home')

class UserNotificationsView(LoginRequiredMixin,ListView):
    model = Notification
    template_name = 'pages/notifications.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        notifications = Notification.objects.filter(recipient=self.request.user)
        notifications.update(is_read=True)
        return notifications

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'Мои уведомления'
        return context

class SnippetsListView(ListView):
    model = Snippet
    template_name = 'pages/snippets_list.html'
    context_object_name = 'snippets'
    paginate_by = 10

    def get_queryset(self):
        snippet_my = self.kwargs.get('snippet_my' ,False)

        if snippet_my:
            if not self.request.user.is_authenticated:
                raise PermissionDenied
            queryset = Snippet.objects.filter(user=self.request.user)
        else:
            if self.request.user.is_authenticated:
                queryset = Snippet.objects.filter(
                    Q(access='public') | Q(access='private', user=self.request.user)
                ).select_related("user")
            else:
                queryset = Snippet.objects.filter(access="public").select_related("user")


        search = self.request.GET.get("search")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )


        lang = self.request.GET.get("lang")
        if lang:
            queryset = queryset.filter(lang=lang)

        user_id = self.request.GET.get("user_id")
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        sort = self.request.GET.get("sort")
        if sort:
            queryset = queryset.order_by(sort)

        tag = self.request.GET.get("tag")
        if tag:
            queryset = queryset.filter(tags__name=tag)


        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        snippet_my = self.kwargs.get('snippet_my', False)
        tag = self.request.GET.get("tag")

        if snippet_my:
            context['pagename'] = 'Мои сниппеты'
        elif tag:
            context['pagename'] = 'Сниппеты по выбранным тегам'
        else:
            context['pagename'] = "Список всех сниппетов"

        lang = self.request.GET.get("lang")
        user_id = self.request.GET.get("user_id")
        filtering = any([lang, user_id])
        if filtering and not self.object_list.exists():
            empty_list = 'no_result'
        else:
            empty_list = 'no_data'

        users = User.objects.annotate(num_snippets=Count('snippet', filter=Q(snippet__access='public'))).filter(
            num_snippets__gt=0).order_by("-num_snippets")

        context.update({
            'sort': self.request.GET.get("sort"),
            'lang': lang,
            'tag': tag,
            'user_id': user_id,
            'LANG_CHOICES': LANG_CHOICES,
            'users': users,
            'snippet_my': snippet_my,
            'empty_list': empty_list,
            'total_snippet' : self.get_queryset().count()
        })

        return context

class SnippetEditView(LoginRequiredMixin, UpdateView):
    model = Snippet
    form_class = SnippetForm
    template_name = 'pages/snippet_add_or_edit.html'
    success_url = reverse_lazy('snippets-mylist')
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        obj = super().get_object()
        if obj.user != self.request.user:
            messages.error(self.request, "У вас нету доступа на изменения")
            return redirect('snippets-list')
        return super().dispatch( request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'Редактирование cниппета'
        context['edit'] = True
        context['id'] = self.kwargs.get("id")
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Сниппет изменен')
        return super().form_valid(form)

