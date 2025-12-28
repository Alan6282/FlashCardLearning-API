from django.db import models
from django.db.models import Index
from django.contrib.auth.models import AbstractUser


# Custom user model with additional profile fields
class CustomUser(AbstractUser):
    cards_reviwed = models.PositiveIntegerField(default=0)
    mastered_cards = models.PositiveIntegerField(default=0)
   

    def  __str__(self):
        return f"{self.username} (Mastered Cards:{self.mastered_cards})"

    class Meta:
        indexes = [
            Index(fields=['username'],name='username_idx'),
        ]


