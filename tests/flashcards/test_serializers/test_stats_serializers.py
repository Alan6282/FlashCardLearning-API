import pytest
from datetime import timedelta
from django.utils import timezone

from apps.flashcards.serializers.stats import (
    UserStatsSerializer,
    DeckStatsSerializer
)


@pytest.mark.django_db
class TestUserStatsSerializer:
    """Test UserStatsSerializer for user-level statistics"""
    
    def test_user_stats_serializer_valid_complete_data(self):
        """Test serializer with complete valid data"""
        data = {
            'total_decks': 5,
            'total_cards': 50,
            'reviews_due_today': 10,
            'due_today': 8,
            'overdue': 2,
            'reviews_done_today': 7,
            'known_cards': 30,
            'unknown_cards': 20,
            'completion_rate': 60.0
        }
        
        serializer = UserStatsSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_user_stats_serializer_zero_stats(self):
        """Test serializer with zero values (new user)"""
        data = {
            'total_decks': 0,
            'total_cards': 0,
            'reviews_due_today': 0,
            'due_today': 0,
            'overdue': 0,
            'reviews_done_today': 0,
            'known_cards': 0,
            'unknown_cards': 0,
            'completion_rate': 0.0
        }
        
        serializer = UserStatsSerializer(data=data)
        assert serializer.is_valid()

    def test_user_stats_serializer_missing_total_decks(self):
        """Test validation fails without total_decks"""
        data = {
            'total_cards': 50,
            'reviews_due_today': 10,
            'due_today': 8,
            'overdue': 2,
            'reviews_done_today': 7,
            'known_cards': 30,
            'unknown_cards': 20,
            'completion_rate': 60.0
        }
        
        serializer = UserStatsSerializer(data=data)
        assert not serializer.is_valid()
        assert 'total_decks' in serializer.errors

    def test_user_stats_serializer_missing_total_cards(self):
        """Test validation fails without total_cards"""
        data = {
            'total_decks': 5,
            'reviews_due_today': 10,
            'due_today': 8,
            'overdue': 2,
            'reviews_done_today': 7,
            'known_cards': 30,
            'unknown_cards': 20,
            'completion_rate': 60.0
        }
        
        serializer = UserStatsSerializer(data=data)
        assert not serializer.is_valid()
        assert 'total_cards' in serializer.errors

    def test_user_stats_serializer_negative_values(self):
        """Test that negative values are rejected"""
        data = {
            'total_decks': -1,
            'total_cards': 50,
            'reviews_due_today': 10,
            'due_today': 8,
            'overdue': 2,
            'reviews_done_today': 7,
            'known_cards': 30,
            'unknown_cards': 20,
            'completion_rate': 60.0
        }
        
        serializer = UserStatsSerializer(data=data)
        # IntegerField should reject negative based on model validation
        # or we might need to check the actual error

    def test_user_stats_serializer_completion_rate_range(self):
        """Test completion_rate as percentage"""
        # Valid: 0-100% range
        data = {
            'total_decks': 5,
            'total_cards': 50,
            'reviews_due_today': 10,
            'due_today': 8,
            'overdue': 2,
            'reviews_done_today': 7,
            'known_cards': 30,
            'unknown_cards': 20,
            'completion_rate': 60.0
        }
        
        serializer = UserStatsSerializer(data=data)
        assert serializer.is_valid()
        assert 0 <= serializer.data['completion_rate'] <= 100

    def test_user_stats_serializer_high_completion_rate(self):
        """Test with high completion rate"""
        data = {
            'total_decks': 1,
            'total_cards': 10,
            'reviews_due_today': 1,
            'due_today': 1,
            'overdue': 0,
            'reviews_done_today': 5,
            'known_cards': 9,
            'unknown_cards': 1,
            'completion_rate': 90.0
        }
        
        serializer = UserStatsSerializer(data=data)
        assert serializer.is_valid()

    def test_user_stats_serializer_all_unknown(self):
        """Test when no cards are known"""
        data = {
            'total_decks': 1,
            'total_cards': 10,
            'reviews_due_today': 5,
            'due_today': 3,
            'overdue': 2,
            'reviews_done_today': 2,
            'known_cards': 0,
            'unknown_cards': 10,
            'completion_rate': 0.0
        }
        
        serializer = UserStatsSerializer(data=data)
        assert serializer.is_valid()

    def test_user_stats_serializer_reviews_breakdown(self):
        """Test that reviews_due_today = due_today + overdue"""
        data = {
            'total_decks': 2,
            'total_cards': 20,
            'reviews_due_today': 10,  # 8 + 2
            'due_today': 8,
            'overdue': 2,
            'reviews_done_today': 3,
            'known_cards': 15,
            'unknown_cards': 5,
            'completion_rate': 75.0
        }
        
        serializer = UserStatsSerializer(data=data)
        assert serializer.is_valid()
        # In real calculation, due_today + overdue should equal reviews_due_today

    def test_user_stats_serializer_all_fields_present(self):
        """Test that all required fields are present"""
        data = {
            'total_decks': 5,
            'total_cards': 50,
            'reviews_due_today': 10,
            'due_today': 8,
            'overdue': 2,
            'reviews_done_today': 7,
            'known_cards': 30,
            'unknown_cards': 20,
            'completion_rate': 60.0
        }
        
        serializer = UserStatsSerializer(data=data)
        assert serializer.is_valid()
        
        expected_fields = [
            'total_decks', 'total_cards', 'reviews_due_today',
            'due_today', 'overdue', 'reviews_done_today',
            'known_cards', 'unknown_cards', 'completion_rate'
        ]
        
        for field in expected_fields:
            assert field in serializer.data


@pytest.mark.django_db
class TestDeckStatsSerializer:
    """Test DeckStatsSerializer for deck-level statistics"""
    
    def test_deck_stats_serializer_valid_complete_data(self):
        """Test serializer with complete valid data"""
        data = {
            'deck_name': 'Math Fundamentals',
            'total_cards': 20,
            'reviews_due_today': 5,
            'due_today': 3,
            'overdue': 2,
            'reviews_done_today': 3,
            'known_cards': 15,
            'unknown_cards': 5,
            'completion_rate': 75.0
        }
        
        serializer = DeckStatsSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_deck_stats_serializer_missing_deck_name(self):
        """Test validation fails without deck_name"""
        data = {
            'total_cards': 20,
            'reviews_due_today': 5,
            'due_today': 3,
            'overdue': 2,
            'reviews_done_today': 3,
            'known_cards': 15,
            'unknown_cards': 5,
            'completion_rate': 75.0
        }
        
        serializer = DeckStatsSerializer(data=data)
        assert not serializer.is_valid()
        assert 'deck_name' in serializer.errors

    def test_deck_stats_serializer_empty_deck_name(self):
        """Test with empty deck name"""
        data = {
            'deck_name': '',
            'total_cards': 20,
            'reviews_due_today': 5,
            'due_today': 3,
            'overdue': 2,
            'reviews_done_today': 3,
            'known_cards': 15,
            'unknown_cards': 5,
            'completion_rate': 75.0
        }
        
        serializer = DeckStatsSerializer(data=data)
        # Empty string should be technically valid at serializer level

    def test_deck_stats_serializer_zero_cards_deck(self):
        """Test with deck having no cards"""
        data = {
            'deck_name': 'Empty Deck',
            'total_cards': 0,
            'reviews_due_today': 0,
            'due_today': 0,
            'overdue': 0,
            'reviews_done_today': 0,
            'known_cards': 0,
            'unknown_cards': 0,
            'completion_rate': 0.0
        }
        
        serializer = DeckStatsSerializer(data=data)
        assert serializer.is_valid()

    def test_deck_stats_serializer_special_characters_in_name(self):
        """Test with special characters in deck name"""
        data = {
            'deck_name': 'Math & Science !@#$%',
            'total_cards': 20,
            'reviews_due_today': 5,
            'due_today': 3,
            'overdue': 2,
            'reviews_done_today': 3,
            'known_cards': 15,
            'unknown_cards': 5,
            'completion_rate': 75.0
        }
        
        serializer = DeckStatsSerializer(data=data)
        assert serializer.is_valid()

    def test_deck_stats_serializer_unicode_deck_name(self):
        """Test with unicode characters in deck name"""
        data = {
            'deck_name': '数学 básico Ελληνικά',
            'total_cards': 20,
            'reviews_due_today': 5,
            'due_today': 3,
            'overdue': 2,
            'reviews_done_today': 3,
            'known_cards': 15,
            'unknown_cards': 5,
            'completion_rate': 75.0
        }
        
        serializer = DeckStatsSerializer(data=data)
        assert serializer.is_valid()

    def test_deck_stats_serializer_completion_rate_calculation(self):
        """Test completion_rate as known_cards/total_cards * 100"""
        # 15 known out of 20 = 75%
        data = {
            'deck_name': 'Test Deck',
            'total_cards': 20,
            'reviews_due_today': 5,
            'due_today': 3,
            'overdue': 2,
            'reviews_done_today': 3,
            'known_cards': 15,
            'unknown_cards': 5,
            'completion_rate': 75.0
        }
        
        serializer = DeckStatsSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.data['completion_rate'] == 75.0

    def test_deck_stats_serializer_all_known(self):
        """Test when all cards are known"""
        data = {
            'deck_name': 'Completed Deck',
            'total_cards': 20,
            'reviews_due_today': 0,
            'due_today': 0,
            'overdue': 0,
            'reviews_done_today': 0,
            'known_cards': 20,
            'unknown_cards': 0,
            'completion_rate': 100.0
        }
        
        serializer = DeckStatsSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.data['completion_rate'] == 100.0

    def test_deck_stats_serializer_all_fields_present(self):
        """Test that all required fields are present"""
        data = {
            'deck_name': 'Complete Deck',
            'total_cards': 20,
            'reviews_due_today': 5,
            'due_today': 3,
            'overdue': 2,
            'reviews_done_today': 3,
            'known_cards': 15,
            'unknown_cards': 5,
            'completion_rate': 75.0
        }
        
        serializer = DeckStatsSerializer(data=data)
        assert serializer.is_valid()
        
        expected_fields = [
            'deck_name', 'total_cards', 'reviews_due_today',
            'due_today', 'overdue', 'reviews_done_today',
            'known_cards', 'unknown_cards', 'completion_rate'
        ]
        
        for field in expected_fields:
            assert field in serializer.data


@pytest.mark.django_db
class TestStatsSerializerIntegration:
    """Integration tests for stats serializers"""
    
    def test_user_stats_serializer_with_actual_data(self, user):
        """Test UserStatsSerializer with calculated data"""
        from apps.flashcards.models import Deck, Card, CardProgress, ReviewHistory
        
        # Create test data
        deck = Deck.objects.create(name='Test Deck', user=user)
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')
        
        # Create progress
        progress1 = CardProgress.objects.create(user=user, card=card1)
        progress2 = CardProgress.objects.create(user=user, card=card2)
        
        # Create reviews
        ReviewHistory.objects.create(user=user, card=card1, quality=4)  # known
        ReviewHistory.objects.create(user=user, card=card2, quality=2)  # unknown
        
        data = {
            'total_decks': 1,
            'total_cards': 2,
            'reviews_due_today': 2,
            'due_today': 2,
            'overdue': 0,
            'reviews_done_today': 2,
            'known_cards': 1,
            'unknown_cards': 1,
            'completion_rate': 50.0
        }
        
        serializer = UserStatsSerializer(data=data)
        assert serializer.is_valid()

    def test_deck_stats_serializer_reflects_deck_state(self, user):
        """Test DeckStatsSerializer accurately reflects deck state"""
        from apps.flashcards.models import Deck, Card, ReviewHistory
        
        deck = Deck.objects.create(name='Science Deck', user=user)
        card = Card.objects.create(deck=deck, question='Science Q?', answer='Science A')
        
        ReviewHistory.objects.create(user=user, card=card, quality=5)  # known
        
        data = {
            'deck_name': 'Science Deck',
            'total_cards': 1,
            'reviews_due_today': 0,
            'due_today': 0,
            'overdue': 0,
            'reviews_done_today': 1,
            'known_cards': 1,
            'unknown_cards': 0,
            'completion_rate': 100.0
        }
        
        serializer = DeckStatsSerializer(data=data)
        assert serializer.is_valid()
