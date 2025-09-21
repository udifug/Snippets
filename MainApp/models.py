from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

LANG_CHOICES = [
    ("python", "Python"),
    ("cpp", "C++"),
    ("java", "Java"),
    ("javascript", "JavaScript")
]

LANG_ICONS = {
    "python": "fa-brands fa-python",
    "cpp": "fa-solid fa-c",
    "java": "fa-brands fa-java",
    "javascript": "fa-brands fa-js",
}

ACCESS_CHOICES = [
    ("public", "Публичный"),
    ("private", "Приватный"),
]

User._meta.get_field('email')._unique = True

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('comment', 'Новый комментарий'),
        ('like', 'Новый лайк'),
        ('follow', 'Новый подписчик'),
        ('snippet_update', 'Обновление сниппета')
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["recipient", "created_at"])
        ]

    def __str__(self):
        return f"Уведомление для {self.recipient.username}: {self.title}"


class LikeDislike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VOTES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    )

    vote = models.SmallIntegerField(choices=VOTES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ['user', 'content_type', 'object_id']


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Snippet(models.Model):
    name = models.CharField(max_length=100)
    lang = models.CharField(max_length=30, choices=LANG_CHOICES)
    code = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True)
    access = models.CharField(max_length=30, choices=ACCESS_CHOICES, default='public')
    tags = models.ManyToManyField(to=Tag)

    def __repr__(self):
        return f"S: {self.name}|{self.lang} views:{self.views_count} public:{self.access} user:{self.user}"

    class Meta:
        indexes = [
            models.Index(fields=["name", "lang"]),
            models.Index(fields=["user", "name", "lang"])
        ]


class Comment(models.Model):
    text = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    snippet = models.ForeignKey(to=Snippet, on_delete=models.CASCADE, related_name="comments")
    likes = GenericRelation(LikeDislike)

    def __repr__(self):
        return f"C: {self.text[:10]} author:{self.author} sn: {self.snippet.name}"

    @classmethod
    def with_likes_count(cls):
        return cls.objects.annotate(
            likes_count=models.Count('likes',
                                     filter=models.Q(likes__vote=LikeDislike.LIKE)),
            dislikes_count=models.Count('likes',
                                        filter=models.Q(likes__vote=LikeDislike.DISLIKE))
        )

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'

    def __str__(self):
        return f"Профиль {self.user.username}"

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscription')
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name='subscription')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'snippet']