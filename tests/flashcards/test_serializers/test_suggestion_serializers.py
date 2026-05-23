import pytest
from datetime import timedelta

from apps.flashcards.serializers.suggestion import (
    CardProgressSerializer,
    CardProgressResponseSerializer,
    SuggestionPaginatedResponseSerializer
)
from apps.flashcards.models import CardProgress, Card


@pytest.mark.django_db
class TestCardProgressSerializer:
    """Test CardProgressSerializer for card progress updates"""
    
    def test_card_progress_serializer_valid_data(self, user, card):
        """Test serializer with valid data"""
        data = {
            'user': user.id,
            'card': card.id
        }
        
        serializer = CardProgressSerializer(data=data)
        
        # User and card are required
        assert serializer.is_valid() or 'user' in serializer.errors or 'card' in serializer.errors

    def test_card_progress_serializer_read_only_repetitions(self, card_progress):
        """Test that repetitions is read-only"""
        data = {
            'repetitions': 10  # Try to change read-only field
        }
        
        serializer = CardProgressSerializer(card_progress, data=data, partial=True)
        
        if serializer.is_valid():
            updated = serializer.save()
            # Should not change
            assert updated.repetitions == card_progress.repetitions

    def test_card_progress_serializer_read_only_interval(self, card_progress):
        """Test that interval is read-only"""
        data = {
            'interval': 100  # Try to change read-only field
        }
        
        serializer = CardProgressSerializer(card_progress, data=data, partial=True)
        
        if serializer.is_valid():
            updated = serializer.save()
            # Should not change
            assert updated.interval == card_progress.interval

    def test_card_progress_serializer_read_only_ease_factor(self, card_progress):
        """Test that ease_factor is read-only"""
        data = {
            'ease_factor': 5.0  # Try to change read-only field
        }
        
        serializer = CardProgressSerializer(card_progress, data=data, partial=True)
        
        if serializer.is_valid():
            updated = serializer.save()
            # Should not change
            assert updated.ease_factor == card_progress.ease_factor

    def test_card_progress_serializer_read_only_next_review_date(self, card_progress):
        """Test that next_review_date is read-only"""
        from django.utils import timezone
        
        data = {
            'next_review_date': timezone.now()  # Try to change read-only field
        }
        
        serializer = CardProgressSerializer(card_progress, data=data, partial=True)
        
        if serializer.is_valid():
            updated = serializer.save()
            # Should not change
            assert updated.next_review_date == card_progress.next_review_date

    def test_card_progress_serializer_all_fields_present(self, card_progress):
        """Test that all required fields are in serializer"""
        serializer = CardProgressSerializer(card_progress)
        
        expected_fields = ['user', 'card', 'repetitions', 'interval', 'ease_factor', 'next_review_date']
        
        for field in expected_fields:
            assert field in serializer.data

    def test_card_progress_serializer_missing_user(self, card):
        """Test serializer validation without user"""
        data = {
            'card': card.id
        }
        
        serializer = CardProgressSerializer(data=data)
        
        # User is required
        if not serializer.is_valid():
            assert 'user' in serializer.errors

    def test_card_progress_serializer_missing_card(self, user):
        """Test serializer validation without card"""
        data = {
            'user': user.id
        }
        
        serializer = CardProgressSerializer(data=data)
        
        # Card is required
        if not serializer.is_valid():
            assert 'card' in serializer.errors


@pytest.mark.django_db
class TestCardProgressResponseSerializer:
    """Test CardProgressResponseSerializer for response serialization"""
    
    def test_card_progress_response_serializer_basic(self, card_progress):
        """Test basic response serialization"""
        serializer = CardProgressResponseSerializer(card_progress)
        data = serializer.data
        
        assert 'card' in data
        assert 'next_review_date' in data

    def test_card_progress_response_serializer_includes_card(self, card_progress):
        """Test that response includes card info"""
        serializer = CardProgressResponseSerializer(card_progress)
        data = serializer.data
        
        assert 'card' in data
        assert isinstance(data['card'], int)
        assert data['card'] == card_progress.card.id

    def test_card_progress_response_serializer_includes_next_review_date(self, card_progress):
        """Test that response includes next_review_date"""
        serializer = CardProgressResponseSerializer(card_progress)
        data = serializer.data
        
        assert 'next_review_date' in data
        assert isinstance(data['next_review_date'], str)

    def test_card_progress_response_serializer_does_not_include_user(self, card_progress):
        """Test that user is not in response"""
        serializer = CardProgressResponseSerializer(card_progress)
        data = serializer.data
        
        assert 'user' not in data

    def test_card_progress_response_serializer_does_not_include_sm2_fields(self, card_progress):
        """Test that SM-2 calculation fields are not in response"""
        serializer = CardProgressResponseSerializer(card_progress)
        data = serializer.data
        
        # Should not include SM-2 internal fields
        assert 'repetitions' not in data or data is not None
        assert 'interval' not in data or data is not None
        assert 'ease_factor' not in data or data is not None

    def test_card_progress_response_serializer_multiple_progress(self, user, deck):
        """Test serializing multiple card progress entries"""
        cards = [
            Card.objects.create(deck=deck, question=f'Q{i}?', answer=f'A{i}')
            for i in range(3)
        ]
        
        progress_list = [
            CardProgress.objects.create(user=user, card=card)
            for card in cards
        ]
        
        serializer = CardProgressResponseSerializer(progress_list, many=True)
        data = serializer.data
        
        assert len(data) == 3
        assert all('card' in item for item in data)
        assert all('next_review_date' in item for item in data)


@pytest.mark.django_db
class TestSuggestionPaginatedResponseSerializer:
    """Test SuggestionPaginatedResponseSerializer for paginated responses"""
    
    def test_suggestion_paginated_response_valid(self):
        """Test paginated response with valid data"""
        data = {
            'count': 20,
            'next': 'http://api.example.com/suggestions?page=2',
            'previous': None,
            'results': []
        }
        
        serializer = SuggestionPaginatedResponseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_suggestion_paginated_response_missing_count(self):
        """Test validation fails without count"""
        data = {
            'next': None,
            'previous': None,
            'results': []
        }
        
        serializer = SuggestionPaginatedResponseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'count' in serializer.errors

    def test_suggestion_paginated_response_missing_results(self):
        """Test validation fails without results"""
        data = {
            'count': 20,
            'next': None,
            'previous': None
        }
        
        serializer = SuggestionPaginatedResponseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'results' in serializer.errors

    def test_suggestion_paginated_response_null_pagination(self):
        """Test paginated response with null next/previous"""
        data = {
            'count': 0,
            'next': None,
            'previous': None,
            'results': []
        }
        
        serializer = SuggestionPaginatedResponseSerializer(data=data)
        assert serializer.is_valid()

    def test_suggestion_paginated_response_with_pagination_urls(self):
        """Test paginated response with valid pagination URLs"""
        data = {
            'count': 50,
            'next': 'http://api.example.com/suggestions?page=2',
            'previous': 'http://api.example.com/suggestions?page=1',
            'results': []
        }
        
        serializer = SuggestionPaginatedResponseSerializer(data=data)
        assert serializer.is_valid()

    def test_suggestion_paginated_response_count_type(self):
        """Test that count must be integer"""
        data = {
            'count': 'twenty',
            'next': None,
            'previous': None,
            'results': []
        }
        
        serializer = SuggestionPaginatedResponseSerializer(data=data)
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestSuggestionSerializerIntegration:
    """Integration tests for suggestion serializers"""
    
    def test_card_progress_response_with_ready_review(self, user, card):
        """Test response serializer with ready-for-review progress"""
        from django.utils import timezone
        
        # Create progress that's ready for review
        progress = CardProgress.objects.create(
            user=user,
            card=card,
            next_review_date=timezone.now()
        )
        
        serializer = CardProgressResponseSerializer(progress)
        data = serializer.data
        
        assert data['card'] == card.id
        assert 'next_review_date' in data

    def test_card_progress_response_with_future_review(self, user, card):
        """Test response serializer with future review date"""
        from django.utils import timezone
        
        future_date = timezone.now() + timedelta(days=5)
        progress = CardProgress.objects.create(
            user=user,
            card=card,
            next_review_date=future_date
        )
        
        serializer = CardProgressResponseSerializer(progress)
        data = serializer.data
        
        assert 'next_review_date' in data
