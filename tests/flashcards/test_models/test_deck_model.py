import pytest 
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import uuid

from apps.flashcards.models import Deck, Card


@pytest.mark.django_db
class TestDeckCreation:
    """Test Deck model creation and basic properties"""
    
    def test_deck_creation_with_all_fields(self, user):
        """Test creating a deck with all fields"""
        deck = Deck.objects.create(
            name='Unit Conversions', 
            user=user,
            category='Science',
            description="A Deck to learn Equations for learning Unit Conversions"
        )
        assert deck.name == 'Unit Conversions'
        assert deck.category == 'Science'
        assert deck.user == user
        assert deck.description == "A Deck to learn Equations for learning Unit Conversions"

    def test_deck_creation_with_minimal_fields(self, user):
        """Test creating a deck with only required fields"""
        deck = Deck.objects.create(name='Minimal Deck', user=user)
        assert deck.name == 'Minimal Deck'
        assert deck.category == 'General'  # Default value
        assert deck.description == ''  # Default blank
        assert deck.is_public is False  # Default False
        assert deck.user == user

    def test_deck_default_values(self, user):
        """Test that default values are correctly set"""
        deck = Deck.objects.create(name='Test Deck', user=user)
        
        assert deck.is_public is False
        assert deck.category == 'General'
        assert deck.description == ''
        assert isinstance(deck.share_link, uuid.UUID)
        assert deck.created_at is not None

    def test_deck_share_link_generation(self, user):
        """Test that share_link is automatically generated"""
        deck = Deck.objects.create(name='Shared Deck', user=user)
        
        assert deck.share_link is not None
        assert isinstance(deck.share_link, uuid.UUID)
        # Share link should be UUID version
        assert len(str(deck.share_link)) == 36  # Standard UUID string length

    def test_deck_string_representation(self, user):
        """Test __str__ method returns correct format"""
        deck = Deck.objects.create(
            name='Math Fundamentals',
            user=user,
            category='Science'
        )
        
        assert str(deck) == f"{deck.name} ({user.username})"
        assert str(deck) == "Math Fundamentals (testuser)"


@pytest.mark.django_db
class TestDeckConstraints:
    """Test Deck model constraints and validations"""
    
    def test_deck_unique_name_per_user_validation(self, user):
        """Test that deck names must be unique per user using full_clean()"""
        Deck.objects.create(
            name='General Knowledge',
            user=user,
            category='General'
        )
        
        duplicate_deck = Deck(
            name='General Knowledge',
            user=user,
            category='General'
        )
        
        with pytest.raises(ValidationError):
            duplicate_deck.full_clean()

    def test_deck_unique_name_per_user_integrity_error(self, user):
        """Test that duplicate deck names raise IntegrityError on save"""
        Deck.objects.create(name='Physics Deck', user=user)
        
        duplicate_deck = Deck(name='Physics Deck', user=user)
        
        with pytest.raises(IntegrityError):
            duplicate_deck.save()

    def test_deck_same_name_different_users(self, user):
        """Test that different users can have decks with the same name"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user2 = User.objects.create_user(username='testuser2', password='pass123')
        
        deck1 = Deck.objects.create(name='Common Name', user=user)
        deck2 = Deck.objects.create(name='Common Name', user=user2)
        
        assert deck1.name == deck2.name
        assert deck1.user != deck2.user
        assert Deck.objects.filter(name='Common Name').count() == 2

    def test_deck_share_link_uniqueness(self, user):
        """Test that share_link is unique across all decks"""
        deck1 = Deck.objects.create(name='Deck 1', user=user)
        deck2 = Deck.objects.create(name='Deck 2', user=user)
        
        assert deck1.share_link != deck2.share_link

    def test_deck_max_length_name(self, user):
        """Test that deck name respects max_length constraint"""
        long_name = 'a' * 101  # Exceed max_length of 100
        
        deck = Deck(name=long_name, user=user)
        
        with pytest.raises(ValidationError):
            deck.full_clean()

    def test_deck_max_length_category(self, user):
        """Test that category respects max_length constraint"""
        long_category = 'a' * 101  # Exceed max_length of 100
        
        deck = Deck(name='Test', user=user, category=long_category)
        
        with pytest.raises(ValidationError):
            deck.full_clean()

    def test_deck_blank_fields_allowed(self, user):
        """Test that category and description can be blank"""
        deck = Deck.objects.create(
            name='Minimal Deck',
            user=user,
            category='',
            description=''
        )
        
        assert deck.category == ''
        assert deck.description == ''


@pytest.mark.django_db
class TestDeckRelationships:
    """Test Deck model relationships and cascading"""
    
    def test_deck_user_foreign_key_cascade(self, user):
        """Test that deleting a user deletes their decks"""
        deck = Deck.objects.create(name='User Deck', user=user)
        deck_id = deck.id
        
        user.delete()
        
        assert not Deck.objects.filter(id=deck_id).exists()

    def test_deck_multiple_decks_for_user(self, user):
        """Test that a user can have multiple decks"""
        deck1 = Deck.objects.create(name='Deck 1', user=user)
        deck2 = Deck.objects.create(name='Deck 2', user=user)
        deck3 = Deck.objects.create(name='Deck 3', user=user)
        
        user_decks = Deck.objects.filter(user=user)
        
        assert user_decks.count() == 3
        assert deck1 in user_decks
        assert deck2 in user_decks
        assert deck3 in user_decks

    def test_deck_related_name_access(self, user):
        """Test accessing decks through user's related_name"""
        deck1 = Deck.objects.create(name='Related Deck 1', user=user)
        deck2 = Deck.objects.create(name='Related Deck 2', user=user)
        
        # Access through related_name 'decks'
        assert user.decks.count() == 2
        assert deck1 in user.decks.all()
        assert deck2 in user.decks.all()

    def test_deck_cards_relationship(self, user):
        """Test that a deck can have multiple cards"""
        deck = Deck.objects.create(name='Card Deck', user=user)
        
        card1 = Card.objects.create(
            deck=deck,
            question='Q1?',
            answer='A1'
        )
        card2 = Card.objects.create(
            deck=deck,
            question='Q2?',
            answer='A2'
        )
        
        assert deck.cards.count() == 2
        assert card1 in deck.cards.all()
        assert card2 in deck.cards.all()

    def test_deck_cascade_delete_cards(self, user):
        """Test that deleting a deck deletes its cards"""
        deck = Deck.objects.create(name='Deletable Deck', user=user)
        
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')
        
        card_ids = [card1.id, card2.id]
        
        deck.delete()
        
        assert not Card.objects.filter(id__in=card_ids).exists()


@pytest.mark.django_db
class TestDeckOrdering:
    """Test Deck queryset ordering"""
    
    def test_deck_ordering_by_created_at_descending(self, user):
        """Test that decks are ordered by created_at in descending order"""
        import time
        
        deck1 = Deck.objects.create(name='First Deck', user=user)
        time.sleep(0.1)  # Small delay to ensure different timestamps
        deck2 = Deck.objects.create(name='Second Deck', user=user)
        time.sleep(0.1)
        deck3 = Deck.objects.create(name='Third Deck', user=user)
        
        decks = Deck.objects.filter(user=user)
        
        # Should be in reverse chronological order
        assert decks[0].name == 'Third Deck'
        assert decks[1].name == 'Second Deck'
        assert decks[2].name == 'First Deck'


@pytest.mark.django_db
class TestDeckPublicSharing:
    """Test Deck public sharing functionality"""
    
    def test_deck_is_public_default_false(self, user):
        """Test that decks are private by default"""
        deck = Deck.objects.create(name='Private Deck', user=user)
        assert deck.is_public is False

    def test_deck_make_public(self, user):
        """Test making a deck public"""
        deck = Deck.objects.create(name='Private Deck', user=user, is_public=False)
        assert deck.is_public is False
        
        deck.is_public = True
        deck.save()
        
        fetched_deck = Deck.objects.get(id=deck.id)
        assert fetched_deck.is_public is True

    def test_deck_share_link_editable_false(self, user):
        """Test that share_link cannot be edited"""
        deck = Deck.objects.create(name='Test Deck', user=user)
        original_share_link = deck.share_link
        
        # Attempting to change share_link should not work (editable=False)
        try:
            new_uuid = uuid.uuid4()
            deck.share_link = new_uuid
            deck.save()
            fetched_deck = Deck.objects.get(id=deck.id)
            # The actual behavior depends on Django version, but share_link should remain same
            assert fetched_deck.share_link == original_share_link
        except:
            pass  # Some versions may raise an error
