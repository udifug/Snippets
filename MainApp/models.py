from django.db import models
from django.contrib.auth.models import User

LANG_CHOICES = [
    ("python", "Python"),
    ("cpp", "C++"),
    ("java", "Java"),
    ("javascript", "JavaScript")
]

LANG_ICONS = {
    "python": "fa-brands fa-python",
    "cpp": "fa-solid fa-code",
    "java": "fa-brands fa-java",
    "javascript": "fa-brands fa-js",
}

ACCESS_CHOICES = [
    ("public", "Публичный"),
    ("private", "Приватный"),
]

class Snippet(models.Model):
    name = models.CharField(max_length=100)
    lang = models.CharField(max_length=30, choices=LANG_CHOICES)
    code = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, blank=True, null=True)
    access = models.CharField(max_length=30, choices=ACCESS_CHOICES,default='public')

    def __str__(self):
        return self.name

class Comment(models.Model):
    text = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    snippet = models.ForeignKey(to=Snippet, on_delete=models.CASCADE)