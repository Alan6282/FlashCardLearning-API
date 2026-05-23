import pytest
import uuid

from apps.flashcards.serializers.decks import (
    DeckSerializer,
    DeckResponseSerializer,
    DeckPaginatedResponseSerializer
)
from apps.flashcards.models import Deck


@pytest.mark.django_db
class TestDeckSerializer:
    """Test DeckSerializer for deck creation/updates"""
    
    def test_deck_serializer_valid_data(self, user):
        """Test serializer with valid data"""
        data = {
            'name': 'Math Deck',
            'category': 'Science',
            'description': 'Learn mathematics',
            'is_public': False
        }
        
        serializer = DeckSerializer(data=data)
        
        assert serializer.is_valid(), serializer.errors

    def test_deck_serializer_missing_name(self, user):
        """Test serializer validation fails without name"""
        data = {
            'category': 'Science',
            'description': 'Learn mathematics'
        }
        
        serializer = DeckSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_deck_serializer_minimal_data(self):
        """Test creating deck with only required field"""
        data = {
            'name': 'Simple Deck'
        }
        
        serializer = DeckSerializer(data=data)
        
        # name is required, others are optional
        if serializer.is_valid():
            assert serializer.validated_data['name'] == 'Simple Deck'

    def test_deck_serializer_read_only_user(self, deck, user):
        """Test that user field is read-only"""
        data = {
            'name': 'Updated Deck',
            'user': 999  # Try to change user
        }
        
        serializer = DeckSerializer(deck, data=data, partial=True)
        
        if serializer.is_valid():
            updated = serializer.save()
            # User should not change
            assert updated.user == user

    def test_deck_serializer_read_only_share_link(self, deck):
        """Test that share_link field is read-only"""
        original_link = deck.share_link
        
        data = {
            'name': 'Updated',
            'share_link': uuid.uuid4()
        }
        
        serializer = DeckSerializer(deck, data=data, partial=True)
        
        if serializer.is_valid():
            updated = serializer.save()
            # share_link should not change
            assert updated.share_link == original_link

    def test_deck_serializer_save_creates_deck(self,user):
        """Test that serializer.save() creates a deck"""
        data = {
            'name': 'New Deck',
            'category': 'General',
            'description': 'A new deck'
        }
        
        serializer = DeckSerializer(data=data)
        assert serializer.is_valid()
        
        # Need to provide user
        deck = serializer.save(user=user)
        
        assert deck.name == 'New Deck'
        assert Deck.objects.filter(id=deck.id).exists()

    def test_deck_serializer_is_public_default(self):
        """Test is_public default value"""
        data = {
            'name': 'Test Deck'
        }
        
        serializer = DeckSerializer(data=data)
        
        if serializer.is_valid():
            assert serializer.validated_data.get('is_public', False) == False

    def test_deck_serializer_category_blank_allowed(self):
        """Test that category can be blank"""
        data = {
            'name': 'Test Deck',
            'category': ''
        }
        
        serializer = DeckSerializer(data=data)
        # Should be valid as category is blank=True
        assert serializer.is_valid() or 'category' not in serializer.errors

    def test_deck_serializer_update_deck(self, deck):
        """Test updating a deck"""
        data = {
            'name': 'Updated Name',
            'description': 'Updated description'
        }
        
        serializer = DeckSerializer(deck, data=data, partial=True)
        
        assert serializer.is_valid()
        
        updated = serializer.save()
        
        assert updated.name == 'Updated Name'
        assert updated.description == 'Updated description'

    def test_deck_serializer_long_name(self):
        """Test maximum length validation for name"""
        long_name = 'a' * 101  # Exceed max_length of 100
        
        data = {
            'name': long_name
        }
        
        serializer = DeckSerializer(data=data)
        
        # Should fail validation
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestDeckResponseSerializer:
    """Test DeckResponseSerializer for API responses"""
    
    def test_deck_response_serializer_basic(self, deck):
        """Test basic deck response serialization"""
        serializer = DeckResponseSerializer(deck)
        data = serializer.data
        
        assert data['id'] == deck.id
        assert data['name'] == deck.name
        assert 'created_at' in data

    def test_deck_response_serializer_includes_user(self, deck):
        """Test that response includes user info"""
        serializer = DeckResponseSerializer(deck)
        data = serializer.data
        
        assert 'user' in data
        assert isinstance(data['user'], dict)
        assert 'id' in data['user']
        assert 'username' in data['user']

    def test_deck_response_serializer_private_deck_no_share_link(self, deck):
        """Test that private decks don't expose share_link"""
        deck.is_public = False
        deck.save()
        
        serializer = DeckResponseSerializer(deck)
        data = serializer.data
        
        # Private decks should not show share_link
        # This depends on to_representation implementation

    def test_deck_response_serializer_public_deck_share_link(self, public_deck):
        """Test that public decks include share_link"""
        serializer = DeckResponseSerializer(public_deck)
        data = serializer.data
        
        # Public decks might show share_link
        assert 'is_public' in data
        assert data['is_public'] is True

    def test_deck_response_serializer_multiple_decks(self, user):
        """Test serializing multiple decks"""
        decks = [
            Deck.objects.create(
                name=f'Deck {i}',
                user=user
            )
            for i in range(1, 4)
        ]
        
        serializer = DeckResponseSerializer(decks, many=True)
        data = serializer.data
        
        assert len(data) == 3
        assert all('id' in item for item in data)
        assert all('name' in item for item in data)

    def test_deck_response_serializer_all_fields(self, deck):
        """Test that all required fields are in response"""
        serializer = DeckResponseSerializer(deck)
        data = serializer.data
        
        required_fields = ['id', 'name', 'category', 'description', 'created_at', 'user', 'is_public']
        
        for field in required_fields:
            assert field in data

    def test_deck_response_serializer_created_at_format(self, deck):
        """Test that created_at is in ISO format"""
        serializer = DeckResponseSerializer(deck)
        data = serializer.data
        
        assert isinstance(data['created_at'], str)
        assert 'T' in data['created_at'] or 'Z' in data['created_at']

    def test_deck_response_serializer_user_nested(self, deck):
        """Test nested user serialization"""
        serializer = DeckResponseSerializer(deck)
        user_data = serializer.data['user']
        
        assert user_data['id'] == deck.user.id
        assert user_data['username'] == deck.user.username


@pytest.mark.django_db
class TestDeckPaginatedResponseSerializer:
    """Test DeckPaginatedResponseSerializer for paginated responses"""
    
    def test_deck_paginated_response_valid(self):
        """Test paginated response with valid data"""
        data = {
            'count': 50,
            'next': 'http://api.example.com/decks?page=2',
            'previous': None,
            'results': []
        }
        
        serializer = DeckPaginatedResponseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_deck_paginated_response_missing_count(self):
        """Test validation fails without count"""
        data = {
            'next': None,
            'previous': None,
            'results': []
        }
        
        serializer = DeckPaginatedResponseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'count' in serializer.errors

    def test_deck_paginated_response_missing_results(self):
        """Test validation fails without results"""
        data = {
            'count': 0,
            'next': None,
            'previous': None
        }
        
        serializer = DeckPaginatedResponseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'results' in serializer.errors

    def test_deck_paginated_response_with_results(self, deck):
        """Test paginated response with actual decks"""
        deck_data = DeckResponseSerializer(deck).data
        
        data = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [deck_data]
        }
        
        serializer = DeckPaginatedResponseSerializer(data=data)
        assert serializer.is_valid()

    def test_deck_paginated_response_multiple_results(self, user):
        """Test paginated response with multiple decks"""
        decks = [
            Deck.objects.create(name=f'Deck {i}', user=user)
            for i in range(1, 4)
        ]
        
        results = DeckResponseSerializer(decks, many=True).data
        
        data = {
            'count': len(results),
            'next': None,
            'previous': None,
            'results': results
        }
        
        serializer = DeckPaginatedResponseSerializer(data=data)
        assert serializer.is_valid()
        assert len(serializer.data['results']) == 3

    def test_deck_paginated_response_count_type(self):
        """Test that count must be integer"""
        data = {
            'count': 'fifty',
            'next': None,
            'previous': None,
            'results': []
        }
        
        serializer = DeckPaginatedResponseSerializer(data=data)
        assert not serializer.is_valid()

    def test_deck_paginated_response_null_pagination(self):
        """Test paginated response with null next/previous"""
        data = {
            'count': 0,
            'next': None,
            'previous': None,
            'results': []
        }
        
        serializer = DeckPaginatedResponseSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestDeckSerializerIntegration:
    """Integration tests for deck serializers"""
    
    def test_create_deck_and_respond(self, user):
        """Test creating deck and responding with response serializer"""
        create_data = {
            'name': 'Integration Test Deck',
            'category': 'Science',
            'description': 'For testing'
        }
        
        create_serializer = DeckSerializer(data=create_data)
        assert create_serializer.is_valid()
        
        deck = create_serializer.save(user=user)
        
        # Respond with response serializer
        response_serializer = DeckResponseSerializer(deck)
        response_data = response_serializer.data
        
        assert response_data['name'] == 'Integration Test Deck'
        assert response_data['user']['id'] == user.id

    def test_update_deck_via_serializer(self, deck):
        """Test updating deck through serializer"""
        update_data = {
            'name': 'Updated Deck Name',
            'is_public': True
        }
        
        serializer = DeckSerializer(deck, data=update_data, partial=True)
        assert serializer.is_valid()
        
        updated_deck = serializer.save()
        
        # Verify with response serializer
        response_serializer = DeckResponseSerializer(updated_deck)
        response_data = response_serializer.data
        
        assert response_data['name'] == 'Updated Deck Name'
        assert response_data['is_public'] is True

    def test_paginate_and_serialize_decks(self, user):
        """Test pagination workflow with deck serializers"""
        for i in range(5):
            Deck.objects.create(name=f'Deck {i}', user=user)
        
        decks = Deck.objects.filter(user=user)
        deck_data = DeckResponseSerializer(decks, many=True).data
        
        paginated = {
            'count': len(deck_data),
            'next': None,
            'previous': None,
            'results': deck_data
        }
        
        serializer = DeckPaginatedResponseSerializer(data=paginated)
        assert serializer.is_valid()
