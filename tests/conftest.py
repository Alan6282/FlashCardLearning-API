import pytest 

from django.test import RequestFactory # Class which helps you to create request with HTTP methods 

from django.contrib.auth import get_user_model 

from rest_framework.test import APIClient

from apps.flashcards.models import Card, Deck , ReviewHistory , CardProgress



@pytest.fixture
def api_client():

   # Fixture for REST API client 

   return APIClient()


@pytest.fixture
def request_factory():
   
   # Fixture for creating test requests

   return RequestFactory()


@pytest.fixture
def user(db):

   User = get_user_model()

   return User.objects.create_user(

      username='testuser',
      password='testpass123'
   )

@pytest.fixture
def staff_user(db):
   
   # Fixture for creating a staff user 

   User = get_user_model()

   return User.objects.create_user(
      username='staffuser',
      password='staffpass123',
      is_staff=True
   )

@pytest.fixture
def admin_user(db):
   
   # Fixture for creating an admin user 

   User = get_user_model()

   return User.objects.create_superuser(
      username='admin',
      password='adminpass123',
      email='admin@example.com'
   )

@pytest.fixture
def admin_client(api_client, admin_user):

   # Fixture for an admin API Client 
   api_client.force_authenticate(user=admin_user)
   return api_client

@pytest.fixture
def staff_client(api_client, staff_user):

   # Fixture for a staff API client 
   api_client.force_authenticate(user=staff_user)

   return api_client

@pytest.fixture
def user_client(api_client, user):

   # Fixture for a regular user API client
   api_client.force_authenticate(user=user)
   return api_client

@pytest.fixture
def multiple_users(db):
   """Fixture for creating multiple test users"""
   User = get_user_model()
   
   users = [
      User.objects.create_user(username=f'user{i}', password=f'pass{i}')
      for i in range(1, 4)
   ]
   return users

@pytest.fixture
def deck(db, user):
   """Fixture for creating a test deck"""
   return Deck.objects.create(
      user=user,
      name="Math Deck",
      category="Science",
      description="A deck for learning math"
   )

@pytest.fixture
def public_deck(db, user):
   """Fixture for creating a public test deck"""
   return Deck.objects.create(
      user=user,
      name="Public Math",
      category="Science",
      description="A public deck for learning math",
      is_public=True
   )

@pytest.fixture
def multiple_decks(db, user):
   """Fixture for creating multiple decks for a user"""
   decks = [
      Deck.objects.create(
         user=user,
         name=f"Deck {i}",
         category=f"Category {i}",
         description=f"Description for deck {i}"
      )
      for i in range(1, 4)
   ]
   return decks

@pytest.fixture
def card(db, deck):
   """Fixture for creating a test card"""
   return Card.objects.create(
      deck=deck,
      question="What is d/dx(e^x)?",
      answer="e^x"
   )

@pytest.fixture
def multiple_cards(db, deck):
   """Fixture for creating multiple cards in a deck"""
   cards = [
      Card.objects.create(
         deck=deck,
         question=f"Question {i}?",
         answer=f"Answer {i}"
      )
      for i in range(1, 4)
   ]
   return cards

@pytest.fixture
def cards_with_progress(db, user, deck):
   """Fixture for creating cards with progress tracking"""
   cards_data = []
   for i in range(1, 4):
      card = Card.objects.create(
         deck=deck,
         question=f"Q{i}?",
         answer=f"A{i}"
      )
      progress = CardProgress.objects.create(
         user=user,
         card=card,
         repetitions=i,
         interval=i*2,
         ease_factor=2.5 + (i*0.1)
      )
      cards_data.append({'card': card, 'progress': progress})
   return cards_data

@pytest.fixture
def review_history(db, user, card):
   """Fixture for creating a test review history entry"""
   return ReviewHistory.objects.create(
      user=user,
      card=card,
      quality=4  # Quality rating from 0-5
   )

@pytest.fixture
def multiple_review_histories(db, user, card):
   """Fixture for creating multiple review history entries"""
   reviews = [
      ReviewHistory.objects.create(
         user=user,
         card=card,
         quality=quality
      )
      for quality in [2, 3, 4, 5]
   ]
   return reviews

@pytest.fixture
def card_progress(db, user, card):
    """Fixture for creating a test card progress entry"""
    return CardProgress.objects.create(
        user=user,
        card=card
    )
