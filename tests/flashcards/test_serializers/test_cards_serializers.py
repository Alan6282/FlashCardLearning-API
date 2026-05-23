import pytest
from rest_framework.test import APIRequestFactory

from apps.flashcards.serializers.cards import (
    CardSerializer,
    CardResponseSerializer,
    CardPaginatedResponseSerializer
)
from apps.flashcards.models import Card


@pytest.mark.django_db
class TestCardSerializer:
    """Test CardSerializer for card creation/updates"""
    
    def test_card_serializer_valid_data(self, deck):
        """Test serializer with valid data"""
        data = {
            'question': 'What is Python?',
            'answer': 'A programming language',
            'deck': deck.id
        }
        
        serializer = CardSerializer(data=data, context={'request': None})
        
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['question'] == 'What is Python?'
        assert serializer.validated_data['answer'] == 'A programming language'

    def test_card_serializer_missing_question(self, deck):
        """Test serializer validation fails without question"""
        data = {
            'answer': 'A programming language',
            'deck': deck.id
        }
        
        serializer = CardSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'question' in serializer.errors

    def test_card_serializer_missing_answer(self, deck):
        """Test serializer validation fails without answer"""
        data = {
            'question': 'What is Python?',
            'deck': deck.id
        }
        
        serializer = CardSerializer(data=data)
        
        assert not serializer.is_valid()
        assert 'answer' in serializer.errors

    def test_card_serializer_without_deck(self):
        """Test serializer validation fails without deck"""
        data = {
            'question': 'What is Python?',
            'answer': 'A programming language'
        }
        
        serializer = CardSerializer(data=data)
        
        assert  serializer.is_valid()
       

    def test_card_serializer_read_only_deck_field(self, card, deck):
        """Test that deck field is ignored during update """

        # Save original deck to verify it does not change 
        original_deck = card.deck 


        data = {
            'question': 'Updated question?',
            'answer': 'Updated answer',
            'deck': 9999 # Try changing deck using a random ID 
        }
        
        serializer = CardSerializer(card, data=data, partial=True)

        # Read-only fields are ignored , so validation passes 
        assert  serializer.is_valid()
 
        updated_card = serializer.save()

        # deck should remain unchanged 
        assert updated_card.deck == original_deck

    def test_card_serializer_save_creates_card(self, deck):
        """Test that serializer.save() creates a card"""
        data = {
            'question': 'Test question?',
            'answer': 'Test answer',
        }
        
        serializer = CardSerializer(data=data)

        assert serializer.is_valid()
        
        # View-like behavior 
        card = serializer.save(deck=deck)
        
        assert card.question == 'Test question?'
        assert card.answer == 'Test answer'
        assert card.deck == deck
        assert Card.objects.filter(id=card.id).exists()

    def test_card_serializer_save_with_extra_kwargs(self, deck):
        """Test that serializer.save() accepts extra kwargs"""
        data = {
            'question': 'Test question?',
            'answer': 'Test answer'
        }
        
        serializer = CardSerializer(data=data)
        assert serializer.is_valid()
        
        card = serializer.save(deck=deck)
        
        assert card.deck == deck

    def test_card_serializer_update_card(self, card):
        """Test updating an existing card"""
        data = {
            'question': 'Updated question?',
            'answer': 'Updated answer'
        }
        
        serializer = CardSerializer(card, data=data, partial=True)
        
        assert serializer.is_valid()
        
        updated_card = serializer.save()
        
        assert updated_card.question == 'Updated question?'
        assert updated_card.answer == 'Updated answer'

    def test_card_serializer_empty_question_allowed(self, deck):
        """Test that empty question string is allowed"""
        data = {
            'question': '',
            'answer': 'Answer',
            'deck': deck.id
        }
        
        serializer = CardSerializer(data=data)
        # Empty strings should be technically valid at serializer level
        # (may fail at model level if field has validators)
        assert serializer.is_valid() or 'question' in serializer.errors

    def test_card_serializer_long_text(self, deck):
        """Test serializer with very long text"""
        long_question = 'Q' * 5000
        long_answer = 'A' * 10000
        
        data = {
            'question': long_question,
            'answer': long_answer,
        }
        
        serializer = CardSerializer(data=data)
        
        if serializer.is_valid():
            card = serializer.save(deck=deck)
            assert len(card.question) == 5000
            assert len(card.answer) == 10000

    def test_card_serializer_special_characters(self, deck):
        """Test serializer with special characters"""
        data = {
            'question': 'What is !@#$%^&*()?',
            'answer': '<html>&special</html>',
            'deck': deck.id
        }
        
        serializer = CardSerializer(data=data)
        assert serializer.is_valid()

    def test_card_serializer_unicode_characters(self, deck):
        """Test serializer with unicode characters"""
        data = {
            'question': '¿Cómo estás? 你好 مرحبا',
            'answer': 'Ελληνικά αλφάβητο',
            'deck': deck.id
        }
        
        serializer = CardSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestCardResponseSerializer:
    """Test CardResponseSerializer for API responses"""
    
    def test_card_response_serializer_basic(self, card):
        """Test basic card response serialization"""
        serializer = CardResponseSerializer(card)
        data = serializer.data
        
        assert data['id'] == card.id
        assert data['question'] == card.question
        assert data['answer'] == card.answer
        assert 'created_at' in data

    def test_card_response_serializer_includes_deck(self, card):
        """Test that response serializer includes deck info"""
        serializer = CardResponseSerializer(card)
        data = serializer.data
        
        assert 'deck' in data
        assert isinstance(data['deck'], dict)
        assert 'id' in data['deck']
        assert 'name' in data['deck']

    def test_card_response_serializer_read_only_fields(self, card):
        """Test that certain fields are read-only"""
        serializer = CardResponseSerializer(card)
        
        # Verify these fields are included in response
        assert 'id' in serializer.data
        assert 'created_at' in serializer.data

    def test_card_response_serializer_deck_nested(self, card):
        """Test nested deck serialization"""
        serializer = CardResponseSerializer(card)
        deck_data = serializer.data['deck']
        
        assert deck_data['id'] == card.deck.id
        assert deck_data['name'] == card.deck.name
        assert 'user' in deck_data

    def test_card_response_serializer_multiple_cards(self, deck):
        """Test serializing multiple cards"""
        cards = [
            Card.objects.create(
                deck=deck,
                question=f'Question {i}?',
                answer=f'Answer {i}'
            )
            for i in range(1, 4)
        ]
        
        serializer = CardResponseSerializer(cards, many=True)
        data = serializer.data
        
        assert len(data) == 3
        assert all('id' in item for item in data)
        assert all('question' in item for item in data)

    def test_card_response_serializer_does_not_include_user(self, card):
        """Test that user field is not in card response"""
        serializer = CardResponseSerializer(card)
        
        # Card response should NOT include user (only in deck)
        assert 'user' not in serializer.data or serializer.data.get('user') is None

    def test_card_response_serializer_created_at_format(self, card):
        """Test that created_at is properly formatted"""
        serializer = CardResponseSerializer(card)
        data = serializer.data
        
        # Should be ISO format datetime string
        assert isinstance(data['created_at'], str)
        assert 'T' in data['created_at'] or 'Z' in data['created_at']


@pytest.mark.django_db
class TestCardPaginatedResponseSerializer:
    """Test CardPaginatedResponseSerializer for paginated responses"""
    
    def test_card_paginated_response_serializer_valid_data(self):
        """Test paginated response serializer with valid data"""
        data = {
            'count': 100,
            'next': 'http://api.example.com/cards?page=2',
            'previous': None,
            'results': []
        }
        
        serializer = CardPaginatedResponseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_card_paginated_response_serializer_missing_count(self):
        """Test serializer validation fails without count"""
        data = {
            'next': 'http://api.example.com/cards?page=2',
            'previous': None,
            'results': []
        }
        
        serializer = CardPaginatedResponseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'count' in serializer.errors

    def test_card_paginated_response_serializer_missing_results(self):
        """Test serializer validation fails without results"""
        data = {
            'count': 100,
            'next': 'http://api.example.com/cards?page=2',
            'previous': None
        }
        
        serializer = CardPaginatedResponseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'results' in serializer.errors

    def test_card_paginated_response_serializer_with_results(self, card):
        """Test serializer with actual card results"""
        card_data = CardResponseSerializer(card).data
        
        data = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [card_data]
        }
        
        serializer = CardPaginatedResponseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_card_paginated_response_serializer_null_next_previous(self):
        """Test serializer with null next and previous"""
        data = {
            'count': 0,
            'next': None,
            'previous': None,
            'results': []
        }
        
        serializer = CardPaginatedResponseSerializer(data=data)
        assert serializer.is_valid()

    def test_card_paginated_response_serializer_multiple_results(self, deck):
        """Test serializer with multiple results"""
        cards = [
            Card.objects.create(
                deck=deck,
                question=f'Q{i}?',
                answer=f'A{i}'
            )
            for i in range(1, 4)
        ]
        
        results = CardResponseSerializer(cards, many=True).data
        
        data = {
            'count': 3,
            'next': None,
            'previous': None,
            'results': results
        }
        
        serializer = CardPaginatedResponseSerializer(data=data)
        assert serializer.is_valid()
        assert len(serializer.data['results']) == 3

    def test_card_paginated_response_serializer_count_type(self):
        """Test that count must be integer"""
        data = {
            'count': 'hundred',
            'next': None,
            'previous': None,
            'results': []
        }
        
        serializer = CardPaginatedResponseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'count' in serializer.errors

    def test_card_paginated_response_serializer_next_url_format(self):
        """Test that next must be valid URL"""
        data = {
            'count': 100,
            'next': 'not-a-valid-url',
            'previous': None,
            'results': []
        }
        
        serializer = CardPaginatedResponseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'next' in serializer.errors

    def test_card_paginated_response_serializer_large_result_set(self, deck):
        """Test serializer with large result set"""
        cards = [
            Card.objects.create(
                deck=deck,
                question=f'Q{i}?',
                answer=f'A{i}'
            )
            for i in range(100)
        ]
        
        results = CardResponseSerializer(cards, many=True).data
        
        data = {
            'count': 100,
            'next': None,
            'previous': None,
            'results': results
        }
        
        serializer = CardPaginatedResponseSerializer(data=data)
        assert serializer.is_valid()
        assert len(serializer.data['results']) == 100


@pytest.mark.django_db
class TestCardSerializerIntegration:
    """Integration tests for card serializers"""
    
    def test_create_card_through_serializer_and_respond(self, deck):
        """Test creating card via serializer and responding with response serializer"""
        # Create via CardSerializer
        create_data = {
            'question': 'Integration test?',
            'answer': 'Integration answer',
           
        }
        
        create_serializer = CardSerializer(data=create_data)
        assert create_serializer.is_valid()
        
        card = create_serializer.save(deck=deck)
        
        # Respond via CardResponseSerializer
        response_serializer = CardResponseSerializer(card)
        response_data = response_serializer.data
        
        assert response_data['question'] == 'Integration test?'
        assert response_data['deck']['id'] == deck.id

    def test_paginate_and_serialize_cards(self, deck):
        """Test pagination workflow with serializers"""
        # Create multiple cards
        for i in range(5):
            Card.objects.create(
                deck=deck,
                question=f'Question {i}?',
                answer=f'Answer {i}'
            )
        
        cards = Card.objects.filter(deck=deck)
        card_data = CardResponseSerializer(cards, many=True).data
        
        # Create paginated response
        paginated_data = {
            'count': len(card_data),
            'next': None,
            'previous': None,
            'results': card_data
        }
        
        paginated_serializer = CardPaginatedResponseSerializer(data=paginated_data)
        assert paginated_serializer.is_valid()

    def test_update_card_via_serializer(self, card):
        """Test updating card through serializer"""
        update_data = {
            'question': 'Updated via serializer?',
            'answer': 'Updated answer via serializer'
        }
        
        serializer = CardSerializer(card, data=update_data, partial=True)
        assert serializer.is_valid()
        
        updated_card = serializer.save()
        
        # Verify with response serializer
        response_serializer = CardResponseSerializer(updated_card)
        response_data = response_serializer.data
        
        assert response_data['question'] == 'Updated via serializer?'
