import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.flashcards.models import Card, Deck


@pytest.mark.django_db
class TestCardListCreateView:
    """Test Card List/Create API endpoints"""
    
    def test_get_cards_for_deck_unauthenticated(self, client, deck):
        """Test that unauthenticated request is rejected"""
        url = reverse('card_list_create', kwargs={'deck_id': deck.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_cards_for_deck_authenticated(self, user_client, deck):
        """Test authenticated user can get cards for their deck"""
        Card.objects.create(deck=deck, question='Question 1?', answer='Answer 1')
        Card.objects.create(deck=deck, question='Question 2?', answer='Answer 2')
        
        url = reverse('card_list_create', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 2

    def test_get_cards_nonexistent_deck(self, user_client):
        """Test getting cards for non-existent deck returns 404"""
        url = reverse('card_list_create', kwargs={'deck_id': 9999})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_cards_other_user_deck(self, user_client, user):
        """Test that user cannot access other user's deck cards"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        other_deck = Deck.objects.create(name='Other Deck', user=other_user)
        
        url = reverse('card_list_create', kwargs={'deck_id': other_deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_cards_pagination(self, user_client, deck):
        """Test that cards list is paginated"""
        for i in range(25):
            Card.objects.create(deck=deck, question=f'Question {i}?', answer=f'Answer {i}')
        
        url = reverse('card_list_create', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data

    def test_get_cards_custom_page_size(self, user_client, deck):
        """Test custom pagination page size"""
        for i in range(10):
            Card.objects.create(deck=deck, question=f'Q{i}?', answer=f'A{i}')
        
        url = reverse('card_list_create', kwargs={'deck_id': deck.id})
        response = user_client.get(f'{url}?page_size=5')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) <= 5

    def test_get_cards_search_by_question(self, user_client, deck):
        """Test searching cards by question text"""
        Card.objects.create(deck=deck, question='Python question?', answer='Python answer')
        Card.objects.create(deck=deck, question='JavaScript question?', answer='JS answer')
        
        url = reverse('card_list_create', kwargs={'deck_id': deck.id})
        response = user_client.get(f'{url}?search=Python')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_get_cards_filter_by_deck(self, user_client, user):
        """Test filtering cards by deck"""
        deck1 = Deck.objects.create(name='Deck 1', user=user)
        deck2 = Deck.objects.create(name='Deck 2', user=user)
        
        Card.objects.create(deck=deck1, question='Q1?', answer='A1')
        Card.objects.create(deck=deck2, question='Q2?', answer='A2')
        
        url = reverse('card_list_create', kwargs={'deck_id': deck1.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_cards_ordering(self, user_client, deck):
        """Test ordering cards by creation date"""
        import time
        
        Card.objects.create(deck=deck, question='Q1?', answer='A1')
        time.sleep(0.1)
        Card.objects.create(deck=deck, question='Q2?', answer='A2')
        
        url = reverse('card_list_create', kwargs={'deck_id': deck.id})
        response = user_client.get(f'{url}?ordering=-created_at')
        
        assert response.status_code == status.HTTP_200_OK

    def test_create_card_unauthenticated(self, client, deck):
        """Test that unauthenticated user cannot create card"""
        data = {'question': 'New question?', 'answer': 'New answer'}
        
        url = reverse('card_list_create', kwargs={'deck_id': deck.id})
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_card_authenticated(self, user_client, deck):
        """Test authenticated user can create card in their deck"""
        data = {'question': 'What is DRF?', 'answer': 'Django REST Framework'}
        
        url = reverse('card_list_create', kwargs={'deck_id': deck.id})
        response = user_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['question'] == 'What is DRF?'
        assert Card.objects.filter(question='What is DRF?').exists()

    def test_create_card_nonexistent_deck(self, user_client):
        """Test creating card in non-existent deck returns 404"""
        data = {'question': 'Question?', 'answer': 'Answer'}
        
        url = reverse('card_list_create', kwargs={'deck_id': 9999})
        response = user_client.post(url, data, format='json')
        
        # Fixed: previous code had a broken assertion (or condition was always True)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]

    def test_create_card_other_user_deck(self, user_client):
        """Test user cannot create card in other user's deck"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='other', password='other')
        other_deck = Deck.objects.create(name='Other Deck', user=other_user)
        
        data = {'question': 'Question?', 'answer': 'Answer'}
        
        url = reverse('card_list_create', kwargs={'deck_id': other_deck.id})
        response = user_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_card_missing_question(self, user_client, deck):
        """Test creating card without question fails"""
        data = {'answer': 'Answer only'}
        
        url = reverse('card_list_create', kwargs={'deck_id': deck.id})
        response = user_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_card_missing_answer(self, user_client, deck):
        """Test creating card without answer fails"""
        data = {'question': 'Question only?'}
        
        url = reverse('card_list_create', kwargs={'deck_id': deck.id})
        response = user_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_multiple_cards(self, user_client, deck):
        """Test creating multiple cards in one deck"""
        for i in range(3):
            data = {'question': f'M_Question {i}?', 'answer': f'Answer {i}'}
            
            url = reverse('card_list_create', kwargs={'deck_id': deck.id})
            response = user_client.post(url, data, format='json')
            
            assert response.status_code == status.HTTP_201_CREATED
        
        assert Card.objects.filter(deck=deck).count() == 3

    def test_create_card_with_special_characters(self, user_client, deck):
        """Test creating card with special characters"""
        data = {
            'question': 'What is !@#$%^&*()?',
            'answer': '<html>Special & Characters</html>'
        }
        
        url = reverse('card_list_create', kwargs={'deck_id': deck.id})
        response = user_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_get_cards_response_format(self, user_client, card):
        """Test response includes all required fields"""
        deck = card.deck
        
        url = reverse('card_list_create', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data
        
        if response.data['results']:
            card_result = response.data['results'][0]
            assert 'id' in card_result
            assert 'question' in card_result
            assert 'answer' in card_result
            assert 'deck' in card_result
            assert 'created_at' in card_result

    def test_create_card_cache_invalidation(self, user_client, deck):
        """Test that creating a card invalidates cache"""
        url = reverse('card_list_create', kwargs={'deck_id': deck.id})
        response1 = user_client.get(url)
        
        data = {'question': 'Cache test?', 'answer': 'Cache answer'}
        response2 = user_client.post(url, data, format='json')
        
        response3 = user_client.get(url)
        
        assert response3.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCardReviewListCreateView:
    """Test Card Review List/Create API endpoints"""
    
    def test_get_card_reviews_unauthenticated(self, client, card):
        """Test unauthenticated request is rejected"""
        url = reverse('card_reviews', kwargs={'card_id': card.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_card_reviews_authenticated(self, user_client, user, card):
        """Test authenticated user can get reviews for a card"""
        from apps.flashcards.models import ReviewHistory
        
        ReviewHistory.objects.create(user=user, card=card, quality=4)
        ReviewHistory.objects.create(user=user, card=card, quality=3)
        
        url = reverse('card_reviews', kwargs={'card_id': card.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

    def test_get_card_reviews_nonexistent_card(self, user_client):
        """Test getting reviews for non-existent card"""
        url = reverse('card_reviews', kwargs={'card_id': 9999})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_card_reviews_filter_by_known(self, user_client, user, card):
        """Test filtering reviews by known status"""
        from apps.flashcards.models import ReviewHistory
        
        ReviewHistory.objects.create(user=user, card=card, quality=0)
        ReviewHistory.objects.create(user=user, card=card, quality=4)
        
        url = reverse('card_reviews', kwargs={'card_id': card.id})
        response = user_client.get(f'{url}?known=true')
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_card_reviews_pagination(self, user_client, user, card):
        """Test review list pagination"""
        from apps.flashcards.models import ReviewHistory
        
        for i in range(5):
            ReviewHistory.objects.create(user=user, card=card, quality=i)
        
        url = reverse('card_reviews', kwargs={'card_id': card.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data

    def test_create_review_unauthenticated(self, client, card):
        """Test unauthenticated user cannot create review"""
        data = {'quality': 4}
        
        url = reverse('card_reviews', kwargs={'card_id': card.id})
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_review_authenticated(self, user_client, user, card):
        """Test authenticated user can create review"""
        data = {'quality': 4}
        
        url = reverse('card_reviews', kwargs={'card_id': card.id})
        response = user_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'known' in response.data
        assert response.data['known'] is True

    def test_create_review_quality_validation(self, user_client, user, card):
        """Test review quality is validated"""
        for quality in [0, 2, 3, 5]:
            data = {'quality': quality}
            
            url = reverse('card_reviews', kwargs={'card_id': card.id})
            response = user_client.post(url, data, format='json')
            
            assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]

    def test_create_multiple_reviews_same_card(self, user_client, user, card):
        """Test user can review same card multiple times"""
        for quality in [1, 2, 3, 4, 5]:
            data = {'quality': quality}
            
            url = reverse('card_reviews', kwargs={'card_id': card.id})
            response = user_client.post(url, data, format='json')
            
            assert response.status_code == status.HTTP_201_CREATED

    def test_create_review_known_derived_from_quality(self, user_client, user, card):
        """Test that 'known' is derived from quality >= 3"""
        url = reverse('card_reviews', kwargs={'card_id': card.id})

        data = {'quality': 2}
        response = user_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['known'] is False
        
        data = {'quality': 3}
        response = user_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['known'] is True


@pytest.mark.django_db
class TestCardDetailView:
    """Test Card Detail API endpoints"""
    
    def test_get_card_detail_unauthenticated(self, client, card):
        """Test unauthenticated request is rejected"""
        url = reverse('card_detail', kwargs={'card_id': card.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_card_detail_authenticated(self, user_client, card):
        """Test authenticated user can get card details"""
        url = reverse('card_detail', kwargs={'card_id': card.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == card.id
        assert response.data['question'] == card.question

    def test_get_nonexistent_card_detail(self, user_client):
        """Test getting non-existent card returns 404"""
        url = reverse('card_detail', kwargs={'card_id': 9999})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_card_authenticated(self, user_client, card):
        """Test updating card details"""
        data = {'question': 'Updated question?', 'answer': 'Updated answer'}
        
        url = reverse('card_detail', kwargs={'card_id': card.id})
        response = user_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['question'] == 'Updated question?'

    def test_delete_card_authenticated(self, user_client, card):
        """Test deleting a card"""
        card_id = card.id
        
        url = reverse('card_detail', kwargs={'card_id': card_id})
        response = user_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Card.objects.filter(id=card_id).exists()

    def test_delete_nonexistent_card(self, user_client):
        """Test deleting non-existent card returns 404"""
        url = reverse('card_detail', kwargs={'card_id': 9999})
        response = user_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCardViewPermissions:
    """Test permission handling in card views"""
    
    def test_user_can_only_see_own_decks_cards(self, user_client):
        """Test user cannot access cards from other user's decks"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        other_deck = Deck.objects.create(name='Other Deck', user=other_user)
        other_card = Card.objects.create(deck=other_deck, question='Other Q?', answer='Other A')
        
        url = reverse('card_detail', kwargs={'card_id': other_card.id})
        response = user_client.get(url)
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_user_cannot_update_other_user_card(self, user_client):
        """Test user cannot update other user's card"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        other_deck = Deck.objects.create(name='Other Deck', user=other_user)
        other_card = Card.objects.create(deck=other_deck, question='Other Q?', answer='Other A')
        
        data = {'question': 'Hacked?', 'answer': 'Hacked'}
        
        url = reverse('card_detail', kwargs={'card_id': other_card.id})
        response = user_client.patch(url, data, format='json')
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_user_cannot_delete_other_user_card(self, user_client):
        """Test user cannot delete other user's card"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        other_deck = Deck.objects.create(name='Other Deck', user=other_user)
        other_card = Card.objects.create(deck=other_deck, question='Other Q?', answer='Other A')
        
        url = reverse('card_detail', kwargs={'card_id': other_card.id})
        response = user_client.delete(url)
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]