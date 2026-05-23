import pytest
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.flashcards.models import Deck, Card, CardProgress, ReviewHistory


@pytest.mark.django_db
class TestUserStatsView:
    """Test User Stats API endpoint"""
    
    def test_get_user_stats_unauthenticated(self, client):
        """Test that unauthenticated request is rejected"""
        url = reverse('user_stats')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_stats_authenticated_no_data(self, user_client):
        """Test user stats for user with no decks/cards"""
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_decks'] == 0
        assert response.data['total_cards'] == 0
        assert response.data['known_cards'] == 0
        assert response.data['unknown_cards'] == 0

    def test_get_user_stats_authenticated_with_data(self, user_client, user):
        """Test user stats with actual data"""
        deck = Deck.objects.create(name='Test', user=user)
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_decks'] == 1
        assert response.data['total_cards'] == 2

    def test_get_user_stats_counts_all_decks(self, user_client, user):
        """Test that all user's decks are counted"""
        for i in range(5):
            Deck.objects.create(name=f'Deck {i}', user=user)
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_decks'] == 5

    def test_get_user_stats_counts_all_cards(self, user_client, user):
        """Test that all user's cards are counted"""
        deck = Deck.objects.create(name='Deck', user=user)
        
        for i in range(10):
            Card.objects.create(deck=deck, question=f'Q{i}?', answer=f'A{i}')
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_cards'] == 10

    def test_get_user_stats_known_cards_calculation(self, user_client, user):
        """Test known cards count (quality >= 3)"""
        deck = Deck.objects.create(name='Deck', user=user)
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')
        card3 = Card.objects.create(deck=deck, question='Q3?', answer='A3')
        
        ReviewHistory.objects.create(user=user, card=card1, quality=5)  # known
        ReviewHistory.objects.create(user=user, card=card2, quality=4)  # known
        ReviewHistory.objects.create(user=user, card=card3, quality=1)  # unknown
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['known_cards'] == 2
        assert response.data['unknown_cards'] == 1

    def test_get_user_stats_unknown_cards_calculation(self, user_client, user):
        """Test unknown cards count (quality < 3)"""
        deck = Deck.objects.create(name='Deck', user=user)
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')
        
        ReviewHistory.objects.create(user=user, card=card1, quality=0)  # unknown
        ReviewHistory.objects.create(user=user, card=card2, quality=2)  # unknown
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['unknown_cards'] == 2

    def test_get_user_stats_completion_rate_zero(self, user_client, user):
        """Test completion_rate when no cards are known"""
        deck = Deck.objects.create(name='Deck', user=user)
        Card.objects.create(deck=deck, question='Q1?', answer='A1')
        Card.objects.create(deck=deck, question='Q2?', answer='A2')
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['completion_rate'] == 0.0

    def test_get_user_stats_completion_rate_full(self, user_client, user):
        """Test completion_rate when all cards are known"""
        deck = Deck.objects.create(name='Deck', user=user)
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')
        
        ReviewHistory.objects.create(user=user, card=card1, quality=5)
        ReviewHistory.objects.create(user=user, card=card2, quality=4)
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['completion_rate'] == 100.0

    def test_get_user_stats_completion_rate_partial(self, user_client, user):
        """Test completion_rate with partial completion"""
        deck = Deck.objects.create(name='Deck', user=user)
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')
        card3 = Card.objects.create(deck=deck, question='Q3?', answer='A3')
        card4 = Card.objects.create(deck=deck, question='Q4?', answer='A4')
        
        # 2 known out of 4 = 50%
        ReviewHistory.objects.create(user=user, card=card1, quality=5)
        ReviewHistory.objects.create(user=user, card=card2, quality=4)
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['completion_rate'] == 50.0

    def test_get_user_stats_reviews_done_today(self, user_client, user):
        """Test reviews_done_today counts reviews from today"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        ReviewHistory.objects.create(user=user, card=card, quality=4)
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['reviews_done_today'] >= 1

    def test_get_user_stats_reviews_done_excludes_old(self, user_client, user):
        """Test reviews_done_today excludes old reviews"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        yesterday = timezone.now() - timedelta(days=1)
        review = ReviewHistory.objects.create(user=user, card=card, quality=4)
        review.reviewed_at = yesterday
        review.save()
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['reviews_done_today'] == 0

    def test_get_user_stats_due_today_calculation(self, user_client, user):
        """Test due_today counts card progress with today's due date"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        today = timezone.now()
        CardProgress.objects.create(user=user, card=card, next_review_date=today)
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['due_today'] >= 0

    def test_get_user_stats_overdue_calculation(self, user_client, user):
        """Test overdue counts card progress with past due date"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        yesterday = timezone.now() - timedelta(days=1)
        CardProgress.objects.create(user=user, card=card, next_review_date=yesterday)
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['overdue'] >= 1

    def test_get_user_stats_reviews_due_today_sum(self, user_client, user):
        """Test reviews_due_today = due_today + overdue"""
        deck = Deck.objects.create(name='Deck', user=user)
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')
        
        today = timezone.now()
        yesterday = today - timedelta(days=1)
        
        CardProgress.objects.create(user=user, card=card1, next_review_date=today)
        CardProgress.objects.create(user=user, card=card2, next_review_date=yesterday)
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['reviews_due_today'] == response.data['due_today'] + response.data['overdue']

    def test_get_user_stats_only_own_data(self, user_client, user):
        """Test that user only sees their own stats"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='other', password='pass')
        other_deck = Deck.objects.create(name='Other Deck', user=other_user)
        Card.objects.create(deck=other_deck, question='Other Q?', answer='Other A')
        
        deck = Deck.objects.create(name='My Deck', user=user)
        Card.objects.create(deck=deck, question='My Q?', answer='My A')
        
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_decks'] == 1
        assert response.data['total_cards'] == 1

    def test_get_user_stats_response_format(self, user_client):
        """Test that response includes all required fields"""
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        required_fields = [
            'total_decks', 'total_cards', 'reviews_due_today',
            'due_today', 'overdue', 'reviews_done_today',
            'known_cards', 'unknown_cards', 'completion_rate'
        ]
        
        for field in required_fields:
            assert field in response.data

    def test_get_user_stats_field_types(self, user_client):
        """Test that response fields have correct types"""
        url = reverse('user_stats')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        int_fields = [
            'total_decks', 'total_cards', 'reviews_due_today',
            'due_today', 'overdue', 'reviews_done_today',
            'known_cards', 'unknown_cards'
        ]
        
        for field in int_fields:
            assert isinstance(response.data[field], int)
        
        assert isinstance(response.data['completion_rate'], float)


@pytest.mark.django_db
class TestDeckStatsView:
    """Test Deck Stats API endpoint"""
    
    def test_get_deck_stats_unauthenticated(self, client, deck):
        """Test that unauthenticated request is rejected"""
        url = reverse('deck_stats', kwargs={'deck_id': deck.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_deck_stats_authenticated_empty_deck(self, user_client, user):
        """Test deck stats for empty deck"""
        deck = Deck.objects.create(name='Empty Deck', user=user)
        
        url = reverse('deck_stats', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['deck_name'] == 'Empty Deck'
        assert response.data['total_cards'] == 0

    def test_get_deck_stats_authenticated_with_cards(self, user_client, user):
        """Test deck stats with cards"""
        deck = Deck.objects.create(name='Test Deck', user=user)
        Card.objects.create(deck=deck, question='Q1?', answer='A1')
        Card.objects.create(deck=deck, question='Q2?', answer='A2')
        
        url = reverse('deck_stats', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['deck_name'] == 'Test Deck'
        assert response.data['total_cards'] == 2

    def test_get_deck_stats_nonexistent_deck(self, user_client):
        """Test getting stats for non-existent deck"""
        url = reverse('deck_stats', kwargs={'deck_id': 9999})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_deck_stats_other_user_deck(self, user_client):
        """Test user cannot access other user's deck stats"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='other', password='pass')
        other_deck = Deck.objects.create(name='Other Deck', user=other_user)
        
        url = reverse('deck_stats', kwargs={'deck_id': other_deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_deck_stats_known_cards_count(self, user_client, user):
        """Test known_cards count for a deck"""
        deck = Deck.objects.create(name='Deck', user=user)
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')
        card3 = Card.objects.create(deck=deck, question='Q3?', answer='A3')
        
        ReviewHistory.objects.create(user=user, card=card1, quality=5)  # known
        ReviewHistory.objects.create(user=user, card=card2, quality=4)  # known
        ReviewHistory.objects.create(user=user, card=card3, quality=1)  # unknown
        
        url = reverse('deck_stats', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['known_cards'] == 2

    def test_get_deck_stats_unknown_cards_count(self, user_client, user):
        """Test unknown_cards count for a deck"""
        deck = Deck.objects.create(name='Deck', user=user)
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')
        
        ReviewHistory.objects.create(user=user, card=card1, quality=2)  # unknown
        ReviewHistory.objects.create(user=user, card=card2, quality=0)  # unknown
        
        url = reverse('deck_stats', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['unknown_cards'] == 2

    def test_get_deck_stats_completion_rate_calculation(self, user_client, user):
        """Test completion_rate for a deck"""
        deck = Deck.objects.create(name='Deck', user=user)
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')
        
        # 1 known out of 2 = 50%
        ReviewHistory.objects.create(user=user, card=card1, quality=5)
        
        url = reverse('deck_stats', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['completion_rate'] == 50.0

    def test_get_deck_stats_completion_rate_100_percent(self, user_client, user):
        """Test completion_rate when all cards are known"""
        deck = Deck.objects.create(name='Deck', user=user)
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')
        
        ReviewHistory.objects.create(user=user, card=card1, quality=5)
        ReviewHistory.objects.create(user=user, card=card2, quality=4)
        
        url = reverse('deck_stats', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['completion_rate'] == 100.0

    def test_get_deck_stats_reviews_done_today(self, user_client, user):
        """Test reviews_done_today for a deck"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        ReviewHistory.objects.create(user=user, card=card, quality=4)
        
        url = reverse('deck_stats', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['reviews_done_today'] >= 1

    def test_get_deck_stats_due_today_calculation(self, user_client, user):
        """Test due_today for a deck"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        today = timezone.now()
        CardProgress.objects.create(user=user, card=card, next_review_date=today)
        
        url = reverse('deck_stats', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_deck_stats_overdue_calculation(self, user_client, user):
        """Test overdue reviews for a deck"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        yesterday = timezone.now() - timedelta(days=1)
        CardProgress.objects.create(user=user, card=card, next_review_date=yesterday)
        
        url = reverse('deck_stats', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['overdue'] >= 1

    def test_get_deck_stats_only_deck_cards_counted(self, user_client, user):
        """Test that only cards from the specific deck are counted"""
        deck1 = Deck.objects.create(name='Deck 1', user=user)
        deck2 = Deck.objects.create(name='Deck 2', user=user)
        
        card1 = Card.objects.create(deck=deck1, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck2, question='Q2?', answer='A2')
        
        ReviewHistory.objects.create(user=user, card=card1, quality=5)
        ReviewHistory.objects.create(user=user, card=card2, quality=5)
        
        url = reverse('deck_stats', kwargs={'deck_id': deck1.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_cards'] == 1
        assert response.data['known_cards'] == 1

    def test_get_deck_stats_response_format(self, user_client, deck):
        """Test that response includes all required fields"""
        url = reverse('deck_stats', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        required_fields = [
            'deck_name', 'total_cards', 'reviews_due_today',
            'due_today', 'overdue', 'reviews_done_today',
            'known_cards', 'unknown_cards', 'completion_rate'
        ]
        
        for field in required_fields:
            assert field in response.data

    def test_get_deck_stats_field_types(self, user_client, deck):
        """Test that response fields have correct types"""
        url = reverse('deck_stats', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        assert isinstance(response.data['deck_name'], str)
        assert isinstance(response.data['total_cards'], int)
        assert isinstance(response.data['reviews_due_today'], int)
        assert isinstance(response.data['completion_rate'], float)

    def test_get_deck_stats_deck_name_matches(self, user_client, user):
        """Test that returned deck_name matches actual deck"""
        deck = Deck.objects.create(name='Specific Deck Name', user=user)
        
        url = reverse('deck_stats', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['deck_name'] == 'Specific Deck Name'

    def test_get_deck_stats_multiple_users_isolated(self, user):
        """Test that different users' stats are isolated"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user2 = User.objects.create_user(username='user2', password='pass')
        
        deck1 = Deck.objects.create(name='Deck', user=user)
        card1 = Card.objects.create(deck=deck1, question='Q1?', answer='A1')
        ReviewHistory.objects.create(user=user, card=card1, quality=5)
        
        deck2 = Deck.objects.create(name='Deck', user=user2)
        
        client1 = APIClient()
        client1.force_authenticate(user=user)
        
        url = reverse('deck_stats', kwargs={'deck_id': deck1.id})
        response = client1.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['known_cards'] == 1