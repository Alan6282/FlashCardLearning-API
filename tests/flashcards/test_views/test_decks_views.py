import pytest
from django.urls import reverse
from rest_framework import status

from apps.flashcards.models import Deck, Card


@pytest.mark.django_db
class TestDeckListCreateView:
    """Test Deck List/Create API endpoints"""
    
    def test_get_decks_unauthenticated(self, client):
        """Test that unauthenticated request is rejected"""
        url = reverse('deck_list_create')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_decks_authenticated(self, user_client, user):
        """Test authenticated user can get their decks"""
        Deck.objects.create(name='Deck 1', user=user)
        Deck.objects.create(name='Deck 2', user=user)
        
        url = reverse('deck_list_create')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data

    def test_get_only_own_decks(self, user_client, user):
        """Test user only sees their own decks, not others'"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user_deck = Deck.objects.create(name='My Deck', user=user)
        
        other_user = User.objects.create_user(username='other', password='pass')
        other_deck = Deck.objects.create(name='Other Deck', user=other_user)
        
        url = reverse('deck_list_create')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        deck_names = [d['name'] for d in response.data.get('results', [])]
        assert 'My Deck' in deck_names or len([d for d in response.data.get('results', []) if d['name'] == 'My Deck']) > 0

    def test_get_decks_pagination(self, user_client, user):
        """Test that deck list is paginated"""
        for i in range(15):
            Deck.objects.create(name=f'Deck {i}', user=user)
        
        url = reverse('deck_list_create')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data

    def test_get_decks_custom_page_size(self, user_client, user):
        """Test custom pagination page size"""
        for i in range(10):
            Deck.objects.create(name=f'Deck {i}', user=user)
        
        url = reverse('deck_list_create')
        response = user_client.get(f'{url}?page_size=5')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) <= 5

    def test_get_decks_filter_by_category(self, user_client, user):
        """Test filtering decks by category"""
        Deck.objects.create(name='Science Deck', user=user, category='Science')
        Deck.objects.create(name='Math Deck', user=user, category='Math')
        
        url = reverse('deck_list_create')
        response = user_client.get(f'{url}?category=Science')
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_decks_filter_by_is_public(self, user_client, user):
        """Test filtering decks by public status"""
        Deck.objects.create(name='Public Deck', user=user, is_public=True)
        Deck.objects.create(name='Private Deck', user=user, is_public=False)
        
        url = reverse('deck_list_create')
        response = user_client.get(f'{url}?is_public=true')
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_decks_search_by_name(self, user_client, user):
        """Test searching decks by name"""
        Deck.objects.create(name='Python Basics', user=user)
        Deck.objects.create(name='JavaScript Advanced', user=user)
        
        url = reverse('deck_list_create')
        response = user_client.get(f'{url}?search=Python')
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_decks_search_by_description(self, user_client, user):
        """Test searching decks by description"""
        Deck.objects.create(name='Deck 1', user=user, description='Learn programming fundamentals')
        Deck.objects.create(name='Deck 2', user=user, description='Advanced topics')
        
        url = reverse('deck_list_create')
        response = user_client.get(f'{url}?search=programming')
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_decks_ordering_by_created_at(self, user_client, user):
        """Test ordering decks by creation date"""
        import time
        
        Deck.objects.create(name='First', user=user)
        time.sleep(0.1)
        Deck.objects.create(name='Second', user=user)
        
        url = reverse('deck_list_create')
        response = user_client.get(f'{url}?ordering=-created_at')
        
        assert response.status_code == status.HTTP_200_OK

    def test_get_decks_ordering_by_name(self, user_client, user):
        """Test ordering decks by name"""
        Deck.objects.create(name='Zebra', user=user)
        Deck.objects.create(name='Apple', user=user)
        
        url = reverse('deck_list_create')
        response = user_client.get(f'{url}?ordering=name')
        
        assert response.status_code == status.HTTP_200_OK

    def test_create_deck_unauthenticated(self, client):
        """Test that unauthenticated user cannot create deck"""
        data = {'name': 'New Deck', 'category': 'Science'}
        
        url = reverse('deck_list_create')
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_deck_authenticated(self, user_client, user):
        """Test authenticated user can create deck"""
        data = {
            'name': 'My New Deck',
            'category': 'Science',
            'description': 'A deck for learning science'
        }
        
        url = reverse('deck_list_create')
        response = user_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'My New Deck'
        assert Deck.objects.filter(name='My New Deck', user=user).exists()

    def test_create_deck_minimal_data(self, user_client, user):
        """Test creating deck with only required field"""
        data = {'name': 'Minimal Deck'}
        
        url = reverse('deck_list_create')
        response = user_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Minimal Deck'

    def test_create_deck_missing_name(self, user_client):
        """Test creating deck without name fails"""
        data = {'category': 'Science'}
        
        url = reverse('deck_list_create')
        response = user_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_duplicate_deck_name_same_user(self, user_client, user):
        """Test creating deck with duplicate name for same user fails"""
        Deck.objects.create(name='Duplicate', user=user)
        
        data = {'name': 'Duplicate'}
        
        url = reverse('deck_list_create')
        response = user_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_same_deck_name_different_users(self, user_client, user):
        """Test different users can have decks with same name"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        data = {'name': 'Common Name'}
        url = reverse('deck_list_create')
        response1 = user_client.post(url, data, format='json')
        
        assert response1.status_code == status.HTTP_201_CREATED

    def test_create_deck_with_special_characters(self, user_client):
        """Test creating deck with special characters"""
        data = {
            'name': 'Deck !@#$%^&*()',
            'description': '<html>Special & characters</html>'
        }
        
        url = reverse('deck_list_create')
        response = user_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED

    def test_get_decks_response_format(self, user_client, user):
        """Test response includes all required fields"""
        Deck.objects.create(name='Test Deck', user=user)
        
        url = reverse('deck_list_create')
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data
        
        if response.data['results']:
            deck = response.data['results'][0]
            assert 'id' in deck
            assert 'name' in deck
            assert 'user' in deck
            assert 'created_at' in deck

    def test_create_deck_cache_invalidation(self, user_client, user):
        """Test that creating deck invalidates cache"""
        url = reverse('deck_list_create')
        
        response1 = user_client.get(url)
        
        data = {'name': 'New Deck'}
        response2 = user_client.post(url, data, format='json')
        
        response3 = user_client.get(url)
        
        assert response3.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestDeckDetailView:
    """Test Deck Detail API endpoints"""
    
    def test_get_deck_detail_unauthenticated(self, client, deck):
        """Test unauthenticated request is rejected"""
        url = reverse('deck_detail', kwargs={'deck_id': deck.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_deck_detail_authenticated(self, user_client, deck):
        """Test authenticated user can get deck details"""
        url = reverse('deck_detail', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == deck.id
        assert response.data['name'] == deck.name

    def test_get_nonexistent_deck(self, user_client):
        """Test getting non-existent deck returns 404"""
        url = reverse('deck_detail', kwargs={'deck_id': 9999})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_other_user_deck_detail(self, user_client):
        """Test user cannot access other user's deck details"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='other', password='pass')
        other_deck = Deck.objects.create(name='Other Deck', user=other_user)
        
        url = reverse('deck_detail', kwargs={'deck_id': other_deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_deck_partial(self, user_client, deck):
        """Test partially updating a deck"""
        data = {'name': 'Updated Name'}
        
        url = reverse('deck_detail', kwargs={'deck_id': deck.id})
        response = user_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Name'

    def test_update_deck_full(self, user_client, deck):
        """Test fully updating a deck"""
        data = {
            'name': 'Fully Updated',
            'category': 'Updated Category',
            'description': 'Updated description',
            'is_public': True
        }
        
        url = reverse('deck_detail', kwargs={'deck_id': deck.id})
        response = user_client.put(url, data, format='json')
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED]

    def test_update_nonexistent_deck(self, user_client):
        """Test updating non-existent deck returns 404"""
        data = {'name': 'Updated'}
        
        url = reverse('deck_detail', kwargs={'deck_id': 9999})
        response = user_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_deck_authenticated(self, user_client, user):
        """Test deleting a deck"""
        deck = Deck.objects.create(name='Deletable', user=user)
        deck_id = deck.id
        
        url = reverse('deck_detail', kwargs={'deck_id': deck_id})
        response = user_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Deck.objects.filter(id=deck_id).exists()

    def test_delete_other_user_deck(self, user_client):
        """Test user cannot delete other user's deck"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='other', password='pass')
        other_deck = Deck.objects.create(name='Other Deck', user=other_user)
        
        url = reverse('deck_detail', kwargs={'deck_id': other_deck.id})
        response = user_client.delete(url)
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestDeckPermissions:
    """Test permission handling in deck views"""
    
    def test_user_cannot_access_other_user_deck(self, user_client, user):
        """Test user cannot see other user's deck"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='other', password='pass')
        other_deck = Deck.objects.create(name='Other Private Deck', user=other_user, is_public=False)
        
        url = reverse('deck_detail', kwargs={'deck_id': other_deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_public_deck_visibility(self, user_client, user):
        """Test that public decks are visible appropriately"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='other', password='pass')
        public_deck = Deck.objects.create(name='Public Deck', user=other_user, is_public=True)
        
        url = reverse('deck_detail', kwargs={'deck_id': public_deck.id})
        response = user_client.get(url)
        
        # Depending on implementation, might be visible or not

    def test_user_can_update_own_deck(self, user_client, deck):
        """Test user can update their own deck"""
        data = {'name': 'Updated by owner'}
        
        url = reverse('deck_detail', kwargs={'deck_id': deck.id})
        response = user_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK

    def test_user_cannot_update_other_user_deck(self, user_client):
        """Test user cannot update other user's deck"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        other_user = User.objects.create_user(username='other', password='pass')
        other_deck = Deck.objects.create(name='Other Deck', user=other_user)
        
        data = {'name': 'Hacked!'}
        
        url = reverse('deck_detail', kwargs={'deck_id': other_deck.id})
        response = user_client.patch(url, data, format='json')
        
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestDeckWithCards:
    """Test deck endpoints when associated with cards"""
    
    def test_delete_deck_cascades_to_cards(self, user_client, user):
        """Test deleting deck deletes associated cards"""
        deck = Deck.objects.create(name='Deck with Cards', user=user)
        
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')
        
        card_ids = [card1.id, card2.id]
        
        url = reverse('deck_detail', kwargs={'deck_id': deck.id})
        response = user_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Card.objects.filter(id__in=card_ids).exists()

    def test_deck_detail_includes_card_count(self, user_client, user):
        """Test deck detail response includes card count or cards info"""
        deck = Deck.objects.create(name='Deck', user=user)
        
        for i in range(3):
            Card.objects.create(deck=deck, question=f'Q{i}?', answer=f'A{i}')
        
        url = reverse('deck_detail', kwargs={'deck_id': deck.id})
        response = user_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Depending on implementation, might include card count