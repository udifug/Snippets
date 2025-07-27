from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from MainApp import views

urlpatterns = [
    path('', views.index_page, name='home'),
    path('snippets/add', views.snippet_create, name='snippets-add'),
    path('snippets/list', views.snippets_list, {"snippet_my": False}, name='snippets-list'),
    path('snippets/mylist', views.snippets_list, {"snippet_my": True}, name='snippets-mylist'),
    path('snippet/<int:id>', views.snippet_page, name="snippet-page"),
    path('snippet/<int:id>/delete', views.snippet_delete, name="snippet-delete"),
    path('snippet/<int:id>/edit', views.snippet_edit, name="snippet-edit"),
    path('login', views.user_login, name="login"),
    path('logout', views.user_logout, name="logout"),
    path('registration', views.user_registration, name="registration"),
    path('comment/add', views.comment_add, name="comment-add"),

]
