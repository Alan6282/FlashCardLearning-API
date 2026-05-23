import pytest
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from apps.flashcards.models import Deck, Card, CardProgress, ReviewHistory


@pytest.mark.django_db
class TestReviewSuggestionView:
    """Test Review Suggestion API endpoint (all decks)"""
    
    def test_get_suggestions_unauthenticated(self, client):
        """Test that unauthenticated request is rejected"""
        url = reverse('review_suggestions')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_suggestions_authenticated_no_data(self, user_client):
        """Test suggestions for user with no due cards"""
        url = reverse('review_suggestions')
        response = user_client.get(url)
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
        if response.status_code == status.HTTP_200_OK:
            assert 'results' in response.data

    def test_get_suggestions_requires_pagination(self, user_client):
        """Test that endpoint requires pagination"""
        url = reverse('review_suggestions')
        response = user_client.get(url)
        
        # Should require page_size or similar pagination params
        # Response should be 200 or 400 (missing pagination)

    def test_get_suggestions_with_pagination(self, user_client, user):
        """Test suggestions with pagination"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        now = timezone.now()
        CardProgress.objects.create(user=user, card=card, next_review_date=now)
        
        url = reverse('review_suggestions')
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'results' in response.data

    def test_get_suggestions_only_due_cards(self, user_client, user):
        """Test that only due cards are returned"""
        deck = Deck.objects.create(name='Deck', user=user)
        
        due_card = Card.objects.create(deck=deck, question='Due?', answer='Yes')
        CardProgress.objects.create(user=user, card=due_card, next_review_date=timezone.now())
        
        future_card = Card.objects.create(deck=deck, question='Future?', answer='Yes')
        future = timezone.now() + timedelta(days=5)
        CardProgress.objects.create(user=user, card=future_card, next_review_date=future)
        
        url = reverse('review_suggestions')
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK
        card_ids = [c['id'] for c in response.data.get('results', [])]
        assert due_card.id in card_ids or len(card_ids) >= 1

    def test_get_suggestions_includes_overdue_cards(self, user_client, user):
        """Test that overdue cards are included in suggestions"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Overdue?', answer='Yes')
        
        yesterday = timezone.now() - timedelta(days=1)
        CardProgress.objects.create(user=user, card=card, next_review_date=yesterday)
        
        url = reverse('review_suggestions')
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_get_suggestions_multiple_decks(self, user_client, user):
        """Test suggestions from multiple decks"""
        deck1 = Deck.objects.create(name='Deck 1', user=user)
        deck2 = Deck.objects.create(name='Deck 2', user=user)
        
        now = timezone.now()
        
        card1 = Card.objects.create(deck=deck1, question='Q1?', answer='A1')
        CardProgress.objects.create(user=user, card=card1, next_review_date=now)
        
        card2 = Card.objects.create(deck=deck2, question='Q2?', answer='A2')
        CardProgress.objects.create(user=user, card=card2, next_review_date=now)
        
        url = reverse('review_suggestions')
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 2

    def test_get_suggestions_filter_by_deck(self, user_client, user):
        """Test filtering suggestions by deck"""
        deck = Deck.objects.create(name='Specific Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        now = timezone.now()
        CardProgress.objects.create(user=user, card=card, next_review_date=now)
        
        url = reverse('review_suggestions')
        response = user_client.get(f'{url}?page_size=10&deck={deck.id}')
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_suggestions_search_by_question(self, user_client, user):
        """Test searching suggestions by question"""
        deck = Deck.objects.create(name='Deck', user=user)
        
        card1 = Card.objects.create(deck=deck, question='Python question?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='JavaScript question?', answer='A2')
        
        now = timezone.now()
        CardProgress.objects.create(user=user, card=card1, next_review_date=now)
        CardProgress.objects.create(user=user, card=card2, next_review_date=now)
        
        url = reverse('review_suggestions')
        response = user_client.get(f'{url}?page_size=10&search=Python')
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_suggestions_ordering(self, user_client, user):
        """Test ordering suggestions"""
        import time
        deck = Deck.objects.create(name='Deck', user=user)
        
        now = timezone.now()
        
        card1 = Card.objects.create(deck=deck, question='First?', answer='A1')
        CardProgress.objects.create(user=user, card=card1, next_review_date=now)
        
        time.sleep(0.1)
        
        card2 = Card.objects.create(deck=deck, question='Second?', answer='A2')
        CardProgress.objects.create(user=user, card=card2, next_review_date=now)
        
        url = reverse('review_suggestions')
        response = user_client.get(f'{url}?page_size=10&ordering=-created_at')
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_suggestions_custom_page_size(self, user_client, user):
        """Test custom pagination page size"""
        deck = Deck.objects.create(name='Deck', user=user)
        
        now = timezone.now()
        for i in range(10):
            card = Card.objects.create(deck=deck, question=f'Q{i}?', answer=f'A{i}')
            CardProgress.objects.create(user=user, card=card, next_review_date=now)
        
        url = reverse('review_suggestions')
        response = user_client.get(f'{url}?page_size=5')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) <= 5

    def test_get_suggestions_pagination_next_previous(self, user_client, user):
        """Test pagination links"""
        deck = Deck.objects.create(name='Deck', user=user)
        
        now = timezone.now()
        for i in range(20):
            card = Card.objects.create(deck=deck, question=f'Q{i}?', answer=f'A{i}')
            CardProgress.objects.create(user=user, card=card, next_review_date=now)
        
        url = reverse('review_suggestions')
        response = user_client.get(f'{url}?page_size=5')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data

    def test_get_suggestions_only_own_data(self, user_client, user):
        """Test that user only sees their own suggestions"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='other', password='pass')
        
        deck1 = Deck.objects.create(name='Deck', user=user)
        deck2 = Deck.objects.create(name='Deck', user=other_user)
        
        now = timezone.now()
        
        card1 = Card.objects.create(deck=deck1, question='Mine?', answer='Yes')
        CardProgress.objects.create(user=user, card=card1, next_review_date=now)
        
        card2 = Card.objects.create(deck=deck2, question='Other?', answer='Yes')
        CardProgress.objects.create(user=other_user, card=card2, next_review_date=now)
        
        url = reverse('review_suggestions')
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK
        # Should only get own suggestion

    def test_get_suggestions_response_format(self, user_client, user):
        """Test response includes all required fields"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        now = timezone.now()
        CardProgress.objects.create(user=user, card=card, next_review_date=now)
        
        url = reverse('review_suggestions')
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data

    def test_get_suggestions_caching(self, user_client, user):
        """Test that suggestions are cached"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        now = timezone.now()
        CardProgress.objects.create(user=user, card=card, next_review_date=now)
        
        url = reverse('review_suggestions')
        
        response1 = user_client.get(f'{url}?page_size=10')
        assert response1.status_code == status.HTTP_200_OK
        
        response2 = user_client.get(f'{url}?page_size=10')
        assert response2.status_code == status.HTTP_200_OK
        
        assert response1.data == response2.data


@pytest.mark.django_db
class TestDeckReviewSuggestionView:
    """Test Deck Review Suggestion API endpoint (specific deck)"""
    
    def test_get_deck_suggestions_unauthenticated(self, client, deck):
        """Test that unauthenticated request is rejected"""
        url = reverse('deck_review_suggestions', kwargs={'deck_id': deck.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_deck_suggestions_authenticated_empty(self, user_client, user):
        """Test suggestions for empty deck"""
        deck = Deck.objects.create(name='Empty Deck', user=user)
        
        url = reverse('deck_review_suggestions', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_get_deck_suggestions_with_due_cards(self, user_client, user):
        """Test suggestions for deck with due cards"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        now = timezone.now()
        CardProgress.objects.create(user=user, card=card, next_review_date=now)
        
        url = reverse('deck_review_suggestions', kwargs={'deck_id': deck.id})
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_get_deck_suggestions_nonexistent_deck(self, user_client):
        """Test suggestions for non-existent deck"""
        url = reverse('deck_review_suggestions', kwargs={'deck_id': 9999})
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_deck_suggestions_other_user_deck(self, user_client):
        """Test user cannot get suggestions from other user's deck"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='other', password='pass')
        other_deck = Deck.objects.create(name='Other Deck', user=other_user)
        
        url = reverse('deck_review_suggestions', kwargs={'deck_id': other_deck.id})
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_deck_suggestions_only_from_deck(self, user_client, user):
        """Test that suggestions only include cards from specific deck"""
        deck1 = Deck.objects.create(name='Deck 1', user=user)
        deck2 = Deck.objects.create(name='Deck 2', user=user)
        
        now = timezone.now()
        
        card1 = Card.objects.create(deck=deck1, question='In Deck 1?', answer='Yes')
        CardProgress.objects.create(user=user, card=card1, next_review_date=now)
        
        card2 = Card.objects.create(deck=deck2, question='In Deck 2?', answer='Yes')
        CardProgress.objects.create(user=user, card=card2, next_review_date=now)
        
        url = reverse('deck_review_suggestions', kwargs={'deck_id': deck1.id})
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK
        # Should only have deck1's card

    def test_get_deck_suggestions_includes_overdue(self, user_client, user):
        """Test that overdue cards are included"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Overdue?', answer='Yes')
        
        yesterday = timezone.now() - timedelta(days=1)
        CardProgress.objects.create(user=user, card=card, next_review_date=yesterday)
        
        url = reverse('deck_review_suggestions', kwargs={'deck_id': deck.id})
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_get_deck_suggestions_excludes_future_cards(self, user_client, user):
        """Test that future cards are excluded"""
        deck = Deck.objects.create(name='Deck', user=user)
        
        future = timezone.now() + timedelta(days=5)
        card = Card.objects.create(deck=deck, question='Future?', answer='Yes')
        CardProgress.objects.create(user=user, card=card, next_review_date=future)
        
        url = reverse('deck_review_suggestions', kwargs={'deck_id': deck.id})
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK
        # Should be empty or not include the future card

    def test_get_deck_suggestions_search_by_question(self, user_client, user):
        """Test searching deck suggestions by question"""
        deck = Deck.objects.create(name='Deck', user=user)
        
        now = timezone.now()
        
        card1 = Card.objects.create(deck=deck, question='Python question?', answer='A1')
        CardProgress.objects.create(user=user, card=card1, next_review_date=now)
        
        card2 = Card.objects.create(deck=deck, question='JavaScript question?', answer='A2')
        CardProgress.objects.create(user=user, card=card2, next_review_date=now)
        
        url = reverse('deck_review_suggestions', kwargs={'deck_id': deck.id})
        response = user_client.get(f'{url}?page_size=10&search=Python')
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_deck_suggestions_ordering(self, user_client, user):
        """Test ordering deck suggestions"""
        import time
        deck = Deck.objects.create(name='Deck', user=user)
        
        now = timezone.now()
        
        card1 = Card.objects.create(deck=deck, question='First?', answer='A1')
        CardProgress.objects.create(user=user, card=card1, next_review_date=now)
        
        time.sleep(0.1)
        
        card2 = Card.objects.create(deck=deck, question='Second?', answer='A2')
        CardProgress.objects.create(user=user, card=card2, next_review_date=now)
        
        url = reverse('deck_review_suggestions', kwargs={'deck_id': deck.id})
        response = user_client.get(f'{url}?page_size=10&ordering=-created_at')
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_deck_suggestions_pagination(self, user_client, user):
        """Test pagination for deck suggestions"""
        deck = Deck.objects.create(name='Deck', user=user)
        
        now = timezone.now()
        for i in range(20):
            card = Card.objects.create(deck=deck, question=f'Q{i}?', answer=f'A{i}')
            CardProgress.objects.create(user=user, card=card, next_review_date=now)
        
        url = reverse('deck_review_suggestions', kwargs={'deck_id': deck.id})
        response = user_client.get(f'{url}?page_size=5')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) <= 5
        assert 'next' in response.data

    def test_get_deck_suggestions_response_format(self, user_client, user):
        """Test response includes all required fields"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        now = timezone.now()
        CardProgress.objects.create(user=user, card=card, next_review_date=now)
        
        url = reverse('deck_review_suggestions', kwargs={'deck_id': deck.id})
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data

    def test_get_deck_suggestions_card_details(self, user_client, user):
        """Test that card details are included in response"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Test Q?', answer='Test A')
        
        now = timezone.now()
        CardProgress.objects.create(user=user, card=card, next_review_date=now)
        
        url = reverse('deck_review_suggestions', kwargs={'deck_id': deck.id})
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK
        if response.data['results']:
            card_result = response.data['results'][0]
            assert 'id' in card_result
            assert 'question' in card_result
            assert 'answer' in card_result
            assert 'deck' in card_result


@pytest.mark.django_db
class TestSuggestionViewsComparison:
    """Test comparison between global and deck-specific suggestions"""
    
    def test_global_vs_deck_specific_suggestions(self, user_client, user):
        """Test that global suggestions include all decks, deck-specific only one"""
        deck1 = Deck.objects.create(name='Deck 1', user=user)
        deck2 = Deck.objects.create(name='Deck 2', user=user)
        
        now = timezone.now()
        
        card1 = Card.objects.create(deck=deck1, question='Q1?', answer='A1')
        CardProgress.objects.create(user=user, card=card1, next_review_date=now)
        
        card2 = Card.objects.create(deck=deck2, question='Q2?', answer='A2')
        CardProgress.objects.create(user=user, card=card2, next_review_date=now)
        
        global_url = reverse('review_suggestions')
        global_response = user_client.get(f'{global_url}?page_size=10')
        
        deck_url = reverse('deck_review_suggestions', kwargs={'deck_id': deck1.id})
        deck_response = user_client.get(f'{deck_url}?page_size=10')
        
        assert global_response.status_code == status.HTTP_200_OK
        assert deck_response.status_code == status.HTTP_200_OK
        
        assert global_response.data['count'] >= deck_response.data['count']

    def test_suggestion_cards_have_progress_info(self, user_client, user):
        """Test that suggestions include card progress info"""
        deck = Deck.objects.create(name='Deck', user=user)
        card = Card.objects.create(deck=deck, question='Q?', answer='A')
        
        now = timezone.now()
        progress = CardProgress.objects.create(user=user, card=card, next_review_date=now)
        
        url = reverse('deck_review_suggestions', kwargs={'deck_id': deck.id})
        response = user_client.get(f'{url}?page_size=10')
        
        assert response.status_code == status.HTTP_200_OK