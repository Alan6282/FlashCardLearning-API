import pytest
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta

from apps.flashcards.models import ReviewHistory, Card


@pytest.mark.django_db
class TestReviewHistoryCreation:
    """Test ReviewHistory model creation and basic properties"""
    
    def test_reviewHistory_creation_with_quality_3(self, card, user):
        """Test creating review history with quality >= 3"""
        review = ReviewHistory.objects.create(
            user=user,
            card=card,
            quality=3
        )
        
        assert review.quality == 3
        assert review.known is True
        assert review.user == user
        assert review.card == card

    def test_reviewHistory_creation_with_quality_4(self, card, user):
        """Test creating review history with quality 4"""
        review = ReviewHistory.objects.create(
            user=user,
            card=card,
            quality=4
        )
        
        assert review.quality == 4
        assert review.known is True

    def test_reviewHistory_creation_with_quality_5(self, card, user):
        """Test creating review history with quality 5 (perfect)"""
        review = ReviewHistory.objects.create(
            user=user,
            card=card,
            quality=5
        )
        
        assert review.quality == 5
        assert review.known is True

    def test_reviewHistory_creation_with_quality_0(self, card, user):
        """Test creating review history with quality 0 (worst)"""
        review = ReviewHistory.objects.create(
            user=user,
            card=card,
            quality=0
        )
        
        assert review.quality == 0
        assert review.known is False

    def test_reviewHistory_creation_with_default_quality(self, card, user):
        """Test creating review history without specifying quality (default=0)"""
        review = ReviewHistory.objects.create(
            user=user,
            card=card
        )
        
        assert review.quality == 0
        assert review.known is False

    def test_reviewHistory_string_representation(self, card, user):
        """Test __str__ method"""
        review = ReviewHistory.objects.create(
            user=user,
            card=card,
            quality=3
        )
        
        expected_str = f"{user.username} reviewed {card} (q={review.quality})"
        assert str(review) == expected_str

    def test_reviewHistory_reviewed_at_auto_set(self, card, user):
        """Test that reviewed_at is automatically set"""
        before = timezone.now()
        review = ReviewHistory.objects.create(
            user=user,
            card=card,
            quality=4
        )
        after = timezone.now()
        
        assert review.reviewed_at is not None
        assert before <= review.reviewed_at <= after

    def test_reviewHistory_reviewed_at_not_editable_on_subsequent_save(self, card, user):
        """Test that reviewed_at remains unchanged when updating other fields"""
        review = ReviewHistory.objects.create(
            user=user,
            card=card,
            quality=3
        )
        
        original_reviewed_at = review.reviewed_at
        
        # Wait a bit and update quality
        import time
        time.sleep(0.1)
        
        review.quality = 4
        review.save()
        
        # reviewed_at should remain the same
        assert review.reviewed_at == original_reviewed_at


@pytest.mark.django_db
class TestReviewHistoryKnownLogic:
    """Test the 'known' field logic based on quality"""
    
    def test_known_false_when_quality_0(self, card, user):
        """Test known=False when quality=0"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=0)
        assert review.known is False

    def test_known_false_when_quality_1(self, card, user):
        """Test known=False when quality=1"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=1)
        assert review.known is False

    def test_known_false_when_quality_2(self, card, user):
        """Test known=False when quality=2 (just below threshold)"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=2)
        assert review.known is False

    def test_known_true_when_quality_3(self, card, user):
        """Test known=True when quality=3 (at threshold)"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=3)
        assert review.known is True

    def test_known_true_when_quality_4(self, card, user):
        """Test known=True when quality=4"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=4)
        assert review.known is True

    def test_known_true_when_quality_5(self, card, user):
        """Test known=True when quality=5 (perfect)"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=5)
        assert review.known is True

    def test_known_updated_on_quality_change(self, card, user):
        """Test that known is recalculated when quality changes"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=2)
        assert review.known is False
        
        # Update quality to passing
        review.quality = 3
        review.save()
        
        # Fetch from database to verify
        fetched_review = ReviewHistory.objects.get(id=review.id)
        assert fetched_review.known is True

    def test_known_updated_from_high_to_low_quality(self, card, user):
        """Test known changes from True to False when quality decreases"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=5)
        assert review.known is True
        
        review.quality = 1
        review.save()
        
        fetched_review = ReviewHistory.objects.get(id=review.id)
        assert fetched_review.known is False


@pytest.mark.django_db
class TestReviewHistoryRelationships:
    """Test ReviewHistory relationships and cascading"""
    
    def test_reviewHistory_user_foreign_key(self, card, user):
        """Test that review is correctly linked to user"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=4)
        
        assert review.user == user
        assert review.user.id == user.id

    def test_reviewHistory_card_foreign_key(self, card, user):
        """Test that review is correctly linked to card"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=4)
        
        assert review.card == card
        assert review.card.id == card.id

    def test_reviewHistory_user_cascade_delete(self, card, user):
        """Test that deleting user deletes their review history"""
        review1 = ReviewHistory.objects.create(user=user, card=card, quality=4)
        review2 = ReviewHistory.objects.create(user=user, card=card, quality=3)
        
        review_ids = [review1.id, review2.id]
        
        user.delete()
        
        assert not ReviewHistory.objects.filter(id__in=review_ids).exists()

    def test_reviewHistory_card_cascade_delete(self, user):
        """Test that deleting card deletes its review history"""
        from apps.flashcards.models import Deck
        
        deck = Deck.objects.create(name="Test Deck", user=user)
        card = Card.objects.create(
            deck=deck,
            question="Test?",
            answer="Answer"
        )
        
        review1 = ReviewHistory.objects.create(user=user, card=card, quality=4)
        review2 = ReviewHistory.objects.create(user=user, card=card, quality=3)
        
        review_ids = [review1.id, review2.id]
        
        card.delete()
        
        assert not ReviewHistory.objects.filter(id__in=review_ids).exists()

    def test_reviewHistory_user_related_name_access(self, card, user):
        """Test accessing reviews through user's related_name"""
        review1 = ReviewHistory.objects.create(user=user, card=card, quality=4)
        review2 = ReviewHistory.objects.create(user=user, card=card, quality=3)
        
        # Access through related_name 'review_history'
        assert user.review_history.count() >= 2
        assert review1 in user.review_history.all()
        assert review2 in user.review_history.all()

    def test_reviewHistory_card_related_name_access(self, user, card):
        """Test accessing reviews through card's related_name"""
        review1 = ReviewHistory.objects.create(user=user, card=card, quality=4)
        review2 = ReviewHistory.objects.create(user=user, card=card, quality=3)
        
        # Access through related_name 'review_history'
        assert card.review_history.count() == 2
        assert review1 in card.review_history.all()
        assert review2 in card.review_history.all()

    def test_multiple_reviews_same_card(self, user, card):
        """Test that multiple reviews can exist for same card"""
        reviews = [
            ReviewHistory.objects.create(user=user, card=card, quality=q)
            for q in [2, 3, 4, 5, 1]
        ]
        
        assert len(reviews) == 5
        assert all(r.card == card for r in reviews)

    def test_same_user_multiple_reviews_same_card(self, user):
        """Test that same user can review same card multiple times"""
        from apps.flashcards.models import Deck
        
        deck = Deck.objects.create(name="Test", user=user)
        card = Card.objects.create(deck=deck, question="Q?", answer="A")
        
        reviews = [
            ReviewHistory.objects.create(user=user, card=card, quality=q)
            for q in [1, 2, 3, 4, 5]
        ]
        
        assert len(reviews) == 5
        assert ReviewHistory.objects.filter(user=user, card=card).count() == 5


@pytest.mark.django_db
class TestReviewHistoryOrdering:
    """Test ReviewHistory queryset ordering"""
    
    def test_reviews_ordered_by_reviewed_at_descending(self, user, card):
        """Test that reviews are ordered by reviewed_at in descending order (newest first)"""
        import time
        
        review1 = ReviewHistory.objects.create(user=user, card=card, quality=1)
        time.sleep(0.1)
        review2 = ReviewHistory.objects.create(user=user, card=card, quality=2)
        time.sleep(0.1)
        review3 = ReviewHistory.objects.create(user=user, card=card, quality=3)
        
        reviews = ReviewHistory.objects.filter(user=user, card=card)
        
        # Should be in reverse chronological order (newest first)
        assert reviews[0].id == review3.id
        assert reviews[1].id == review2.id
        assert reviews[2].id == review1.id

    def test_multiple_reviews_ordering_complex(self, user):
        """Test ordering with multiple cards and reviews"""
        import time
        from apps.flashcards.models import Deck
        
        deck = Deck.objects.create(name="Deck", user=user)
        card1 = Card.objects.create(deck=deck, question="Q1?", answer="A1")
        card2 = Card.objects.create(deck=deck, question="Q2?", answer="A2")
        
        # Create reviews in specific order
        r1 = ReviewHistory.objects.create(user=user, card=card1, quality=1)
        time.sleep(0.1)
        r2 = ReviewHistory.objects.create(user=user, card=card2, quality=2)
        time.sleep(0.1)
        r3 = ReviewHistory.objects.create(user=user, card=card1, quality=3)
        
        all_reviews = ReviewHistory.objects.all()
        
        # Should be ordered by reviewed_at descending
        assert all_reviews[0].id == r3.id
        assert all_reviews[1].id == r2.id
        assert all_reviews[2].id == r1.id


@pytest.mark.django_db
class TestReviewHistoryQueries:
    """Test ReviewHistory queryset operations"""
    
    def test_filter_by_quality_known(self, user, card):
        """Test filtering reviews where known=True"""
        ReviewHistory.objects.create(user=user, card=card, quality=1)
        ReviewHistory.objects.create(user=user, card=card, quality=2)
        known_review = ReviewHistory.objects.create(user=user, card=card, quality=4)
        
        known_reviews = ReviewHistory.objects.filter(known=True)
        
        assert known_review in known_reviews
        assert known_reviews.count() >= 1

    def test_filter_by_quality_unknown(self, user, card):
        """Test filtering reviews where known=False"""
        unknown_review1 = ReviewHistory.objects.create(user=user, card=card, quality=1)
        unknown_review2 = ReviewHistory.objects.create(user=user, card=card, quality=2)
        ReviewHistory.objects.create(user=user, card=card, quality=4)
        
        unknown_reviews = ReviewHistory.objects.filter(known=False)
        
        assert unknown_review1 in unknown_reviews
        assert unknown_review2 in unknown_reviews

    def test_filter_by_specific_quality(self, user, card):
        """Test filtering by specific quality value"""
        ReviewHistory.objects.create(user=user, card=card, quality=2)
        quality_4_review = ReviewHistory.objects.create(user=user, card=card, quality=4)
        ReviewHistory.objects.create(user=user, card=card, quality=3)
        
        quality_4 = ReviewHistory.objects.filter(quality=4)
        
        assert quality_4_review in quality_4
        assert quality_4.count() >= 1

    def test_filter_by_user(self, user, card):
        """Test filtering reviews by user"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user2 = User.objects.create_user(username='user2', password='pass')
        
        review1 = ReviewHistory.objects.create(user=user, card=card, quality=4)
        review2 = ReviewHistory.objects.create(user=user2, card=card, quality=3)
        
        user_reviews = ReviewHistory.objects.filter(user=user)
        
        assert review1 in user_reviews
        assert review2 not in user_reviews

    def test_filter_by_card(self, user):
        """Test filtering reviews by card"""
        from apps.flashcards.models import Deck
        
        deck = Deck.objects.create(name="Deck", user=user)
        card1 = Card.objects.create(deck=deck, question="Q1?", answer="A1")
        card2 = Card.objects.create(deck=deck, question="Q2?", answer="A2")
        
        review1 = ReviewHistory.objects.create(user=user, card=card1, quality=4)
        review2 = ReviewHistory.objects.create(user=user, card=card2, quality=3)
        
        card1_reviews = ReviewHistory.objects.filter(card=card1)
        
        assert review1 in card1_reviews
        assert review2 not in card1_reviews

    def test_reviews_for_card_average_quality(self, user, card):
        """Test calculating average quality for a card"""
        ReviewHistory.objects.create(user=user, card=card, quality=2)
        ReviewHistory.objects.create(user=user, card=card, quality=4)
        ReviewHistory.objects.create(user=user, card=card, quality=4)
        
        reviews = ReviewHistory.objects.filter(card=card)
        avg_quality = reviews.aggregate(avg=models.Avg('quality'))['avg']
        
        # Average of [2, 4, 4] = 10/3 ≈ 3.33
        assert avg_quality is not None

    def test_count_known_vs_unknown(self, user, card):
        """Test counting known vs unknown reviews"""
        ReviewHistory.objects.create(user=user, card=card, quality=1)
        ReviewHistory.objects.create(user=user, card=card, quality=2)
        ReviewHistory.objects.create(user=user, card=card, quality=3)
        ReviewHistory.objects.create(user=user, card=card, quality=4)
        ReviewHistory.objects.create(user=user, card=card, quality=5)
        
        known_count = ReviewHistory.objects.filter(known=True).count()
        unknown_count = ReviewHistory.objects.filter(known=False).count()
        
        assert unknown_count == 2  # quality 0, 1, 2
        assert known_count == 3    # quality 3, 4, 5


@pytest.mark.django_db
class TestReviewHistoryEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_multiple_reviews_within_short_time(self, user, card):
        """Test creating multiple reviews in quick succession"""
        reviews = []
        for quality in range(0, 6):
            review = ReviewHistory.objects.create(
                user=user,
                card=card,
                quality=quality
            )
            reviews.append(review)
        
        assert len(reviews) == 6
        assert ReviewHistory.objects.filter(card=card).count() == 6

    def test_review_with_zero_quality(self, user, card):
        """Test review with quality 0"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=0)
        
        assert review.quality == 0
        assert review.known is False

    def test_review_modification(self, user, card):
        """Test modifying review fields"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=1)
        original_reviewed_at = review.reviewed_at
        
        review.quality = 5
        review.save()
        
        fetched = ReviewHistory.objects.get(id=review.id)
        
        assert fetched.quality == 5
        assert fetched.known is True
        assert fetched.reviewed_at == original_reviewed_at

    def test_bulk_create_reviews(self, user, card):
        """Test bulk creating multiple reviews"""
        reviews = [
            ReviewHistory(user=user, card=card, quality=q,known=q >= 3)
            for q in [1, 2, 3, 4, 5]
        ]
        
        created_reviews = ReviewHistory.objects.bulk_create(reviews)
        
        assert len(created_reviews) == 5
        
        # Note: bulk_create doesn't call save(), so custom save() logic won't run
        # Need to refresh from database
        for review in ReviewHistory.objects.filter(card=card):
            if review.quality >= 3:
                assert review.known is True
            else:
                assert review.known is False

    def test_review_string_with_special_characters(self, user):
        """Test review string representation with special characters in card"""
        from apps.flashcards.models import Deck
        
        deck = Deck.objects.create(name="Deck", user=user)
        card = Card.objects.create(
            deck=deck,
            question="What is 2+2=4?",
            answer="True & correct!"
        )
        
        review = ReviewHistory.objects.create(user=user, card=card, quality=4)
        
        assert "&" in str(review) or "Card in" in str(review)


# Import models for aggregate query
from django.db import models
