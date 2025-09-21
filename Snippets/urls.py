from django.urls import path
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from MainApp import views, views_cbv
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
                  path('', views.index_page, name='home'),
                  # path('snippets/add', views.snippet_create, name='snippets-add'),
                  path('snippets/add', views_cbv.AddSnippetView.as_view(), name='snippets-add'),
                  # path('snippets/list', views.snippets_list, {"snippet_my": False}, name='snippets-list'),
                  path('snippets/list', views_cbv.SnippetsListView.as_view(), {"snippet_my": False}, name='snippets-list'),
                  # path('snippets/mylist', views.snippets_list, {"snippet_my": True}, name='snippets-mylist'),
                  path('snippets/mylist', views_cbv.SnippetsListView.as_view(), {"snippet_my": True}, name='snippets-mylist'),
                  path('snippets/stats', views.snippets_stats, name='snippets-stats'),
                  # path('snippet/<int:id>', views.snippet_detail, name="snippet-page"),
                  path('snippet/<int:id>', views_cbv.SnippetDetailView.as_view(), name="snippet-page"),
                  path('snippet/<int:id>/delete', views.snippet_delete, name="snippet-delete"),
                  # path('snippet/<int:id>/edit', views.snippet_edit, name="snippet-edit"),
                  path('snippet/<int:id>/edit', views_cbv.SnippetEditView.as_view(), name="snippet-edit"),
                  path('login', views.user_login, name="login"),
                  # path('logout', views.user_logout, name="logout"),
                  path('logout', views_cbv.UserLogoutView.as_view(), name="logout"),
                  path('registration', views.user_registration, name="registration"),
                  path('profile/', views.user_profile, name='user-profile'),
                  path('profile/edit', views.edit_profile, name='edit-profile'),
                  path('comment/add', views.comment_add, name="comment-add"),
                  path('admin/', admin.site.urls),
                  path('snippet/<int:id>/subscribe/', views.subscribe_to_snippet, name='subscribe'),
                  # path('notifications/', views.user_notifications, name="notifications"),
                  path('notifications/', views_cbv.UserNotificationsView.as_view(), name="notifications"),
                  path('api/notifications/unread-count/', views.unread_notifications_count,
                       name='unread-notifications-count'),
                  path('api/comment/like/', views.comment_like, name='comment-like'),
                  path('activate/<int:user_id>/<str:token>/', views.activate_account, name='activate-account')
              ] + debug_toolbar_urls()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
