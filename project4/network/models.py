from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField('self', symmetrical=False, related_name="following", blank=True)

    def follower_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    timestamp = models.DateTimeField(default=now)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")  # Users who liked this post

    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"
