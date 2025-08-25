from django.contrib import admin
from .models import Snippet, Comment, Tag, Notification
from django.db.models import Count

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'title', 'message']
    readonly_fields = ['created_at']

class SnippetAdmin(admin.ModelAdmin):
    list_display = ('name', 'lang', 'access', 'user', 'num_comments')
    list_filter = ('lang', 'access')
    search_fields = ('name',)


    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            num_comments=Count('comments', distinct=True)
        )
        return queryset

    def num_comments(self, obj):
        return obj.num_comments

    num_comments.short_description = 'Кол-во комментариев'
    fields = ('name', 'lang', 'code', 'access', 'user', 'tags')

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name',)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("text", 'author', 'snippet')
    list_filter = ('author', 'snippet')
    search_fields = ('text', 'snippet__name')


admin.site.site_header = "Snippets Admin"
admin.site.site_title = "Snippets Admin Portal"
admin.site.index_title = "Welcome to Snippets Admin Portal"
# Register your models here.
admin.site.register(Snippet, SnippetAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag, TagAdmin)
