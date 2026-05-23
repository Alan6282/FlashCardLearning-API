from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

import uuid

from datetime import timedelta

from django.utils import timezone

from django.db.models import Q

'''
Deck Model Which Stores the info about the cards of Deck created by the user 
'''

class Deck(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="decks")
    name = models.CharField(max_length=100)
    category=models.CharField(max_length=100,blank=True,default="General")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    share_link = models.UUIDField(default=uuid.uuid4,unique=True,editable=False)

    class Meta:
      constraints = [
        models.UniqueConstraint(fields=["user","name"],name="unique_deck_name_per_user")
      ]
      ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.user.username})" 
    

class Card(models.Model):
    deck =  models.ForeignKey(Deck, on_delete=models.CASCADE,related_name="cards")
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~Q(question=""),
                name="question_not_empty"
            ),
            models.CheckConstraint(
            condition=~Q(answer=""),
            name="answer_not_empty"
           )

        ]

    def __str__(self):

        return f"Card in {self.deck.name}: {self.question}"
    



class ReviewHistory(models.Model):

    """
    Stores each review attempt made by a user for a specific card.
    Each row = one review session.

    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="review_history")
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="review_history")

    quality = models.IntegerField(default=0) # 0-5 user rating
    known = models.BooleanField() # Determines Whether the user known it or not based on quality
    reviewed_at = models.DateTimeField(auto_now_add=True) # reviewed time


    class Meta:
        ordering = ["-reviewed_at"]

    def save(self,*args,**kwargs):


        # Derving Known from Quality 
        self.known = self.quality >=3
        super().save(*args,**kwargs)


    def __str__(self):

        return f"{self.user.username} reviewed {self.card} (q={self.quality})"
    



class CardProgress(models.Model):

    """
    Tracks the user's learning progress for each card,
    updated using the SM-2 algorithm after every review.
    
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="card_progress")
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="card_progress")

    # SM-2 Algorithm Fields #

    
    
    repetitions = models.IntegerField(default=0)
    interval = models.IntegerField(default=1)  # days until next review
    ease_factor = models.FloatField(default=2.5)
    next_review_date = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ["user","card"]
    def str(self):

        return f"{self.user.username} - {self.card} | reps={self.repetitions} ,EF={self.ease_factor:.2f} ,I = {self.interval}d"
    


    
    # -- SM-2 Algorithm implementation --
    # -- Review Scheduling --- 
    
    def update_sm2(self,quality):
        """
        Updates the progress state based on SM-2 algorithm rules.
        The 'quality' value comes from the latest review event.

        """


        q = max(0, min(5, int(quality)))  # clamp 0–5
 
        # If the answer quality < 3, restart learning
        if q < 3:
            
            self.repetitions = 0 
            self.interval = 1
        else:
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
               self.interval = 6
            else:
                self.interval = int(self.interval * self.ease_factor)
            self.repetitions += 1

            # update ease factor (only if quality >= 3)

            self.ease_factor += (0.1 - (5 - q) * (0.08 + (5-q) * 0.02)) # ease factor updation formula

            if self.ease_factor < 1.3:
                self.ease_factor = 1.3 # setting the value of ease to 1.3 when it is less than that
            

        # schedule next review
        self.next_review_date = timezone.now() + timedelta(days=self.interval)

        self.save()


        
    
  
    
    
    

    