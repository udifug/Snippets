from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, View, ListView
from MainApp.models import Snippet, Notification
from MainApp.forms import SnippetForm
from django.contrib import messages, auth
from django.shortcuts import  redirect

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
        ...

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        snippet = self.get_object()
        context['pagename'] = f'Сниппет: {snippet.name}'
        return context

class UserLogoutView(View):
    def get(self, request):
        auth.logout(request)
        return redirect('home')

class UserNotificationsView(ListView,LoginRequiredMixin):
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