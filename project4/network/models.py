from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class userPost(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="publisher")
    content = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes
        }
    
class Community(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="profile")
    followers = models.ManyToManyField("User", related_name="user_followers")
    number_of_followers = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user} has {self.number_of_followers} followers"

 

