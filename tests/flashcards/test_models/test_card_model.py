import pytest 
from django.db import IntegrityError

from apps.flashcards.models import Card, ReviewHistory, CardProgress


@pytest.mark.django_db
class TestCardCreation:
    """Test Card model creation and basic properties"""
    
    def test_card_creation(self, deck):
        """Test basic card creation with all fields"""
        card = Card.objects.create(
            question="What is the derivative of sin(x)?",
            answer="cos(x)",
            deck=deck
        )
        
        assert card.question == "What is the derivative of sin(x)?"
        assert card.answer == "cos(x)"
        assert card.deck == deck

    def test_card_creation_with_long_text(self, deck):
        """Test card creation with long question and answer text"""
        long_question = "What is " + "x" * 1000 + "?"
        long_answer = "y" * 1000
        
        card = Card.objects.create(
            question=long_question,
            answer=long_answer,
            deck=deck
        )
        
        assert card.question == long_question
        assert card.answer == long_answer

    def test_card_created_at_auto_set(self, deck):
        """Test that created_at is automatically set"""
        card = Card.objects.create(
            question="Q?",
            answer="A",
            deck=deck
        )
        
        assert card.created_at is not None

    def test_card_string_representation(self, deck):
        """Test __str__ method returns correct format"""
        card = Card.objects.create(
            question="What is Python?",
            answer="A programming language",
            deck=deck
        )
        
        expected_str = f"Card in {deck.name}: {card.question}"
        assert str(card) == expected_str

    def test_card_string_representation_with_special_chars(self, deck):
        """Test __str__ with special characters"""
        card = Card.objects.create(
            question="What is 2+2=4?",
            answer="True & correct!",
            deck=deck
        )
        
        assert str(card) == f"Card in {deck.name}: What is 2+2=4?"


@pytest.mark.django_db
class TestCardRequiredFields:
    """Test that Card model enforces required fields"""
    
    def test_card_missing_question_raises_error(self, deck):
        """Test that missing question raises error"""
        with pytest.raises(IntegrityError):
            Card.objects.create(
                answer="Answer without question",
                deck=deck
            )

    def test_card_missing_answer_raises_error(self, deck):
        """Test that missing answer raises error"""
        with pytest.raises(IntegrityError):
            Card.objects.create(
                question="Question without answer?",
                deck=deck
            )

    def test_card_missing_deck_raises_error(self):
        """Test that missing deck raises error"""
        with pytest.raises(IntegrityError):
            Card.objects.create(
                question="Orphan question?",
                answer="No deck parent"
            )

    def test_card_null_question_not_allowed(self, deck):
        """Test that NULL question is not allowed"""
        card = Card(question=None, answer="A", deck=deck)
        
        with pytest.raises(IntegrityError):
            card.save()

    def test_card_empty_string_question_not_allowed(self, deck):
        """Test that empty string question is not allowed (but not NULL)"""

        with pytest.raises(IntegrityError):  

         card = Card.objects.create(
            question="",
            answer="Answer for empty question",
            deck=deck
         )
        
        
       

    def test_card_empty_string_answer_not_allowed(self, deck):
        """Test that empty string answer is not allowed (but not NULL)"""

        with pytest.raises(IntegrityError):
            card = Card.objects.create(
                question="Question with empty answer?",
                answer="",
                deck=deck
            )
        
        


@pytest.mark.django_db
class TestCardRelationships:
    """Test Card model relationships and cascading"""
    
    def test_card_deck_foreign_key(self, deck):
        """Test that card is correctly linked to deck"""
        card = Card.objects.create(
            question="Test?",
            answer="Test answer",
            deck=deck
        )
        
        assert card.deck == deck
        assert card.deck.id == deck.id

    def test_card_deck_cascade_delete(self, deck):
        """Test that deleting a deck deletes its cards"""
        card1 = Card.objects.create(
            question="Q1?",
            answer="A1",
            deck=deck
        )
        card2 = Card.objects.create(
            question="Q2?",
            answer="A2",
            deck=deck
        )
        
        card_ids = [card1.id, card2.id]
        
        deck.delete()
        
        assert not Card.objects.filter(id__in=card_ids).exists()

    def test_card_related_name_access(self, deck):
        """Test accessing cards through deck's related_name"""
        card1 = Card.objects.create(
            question="Q1?",
            answer="A1",
            deck=deck
        )
        card2 = Card.objects.create(
            question="Q2?",
            answer="A2",
            deck=deck
        )
        
        # Access through related_name 'cards'
        assert deck.cards.count() == 2
        assert card1 in deck.cards.all()
        assert card2 in deck.cards.all()

    def test_multiple_cards_same_deck(self, deck):
        """Test that multiple cards can exist in same deck"""
        cards = [
            Card.objects.create(
                question=f"Question {i}?",
                answer=f"Answer {i}",
                deck=deck
            )
            for i in range(1, 6)
        ]
        
        assert deck.cards.count() == 5
        assert all(card.deck == deck for card in cards)

    def test_card_same_content_different_decks(self, user):
        """Test that same question/answer can exist in different decks"""
        from apps.flashcards.models import Deck
        
        deck1 = Deck.objects.create(name="Deck 1", user=user)
        deck2 = Deck.objects.create(name="Deck 2", user=user)
        
        card1 = Card.objects.create(
            question="Duplicate question?",
            answer="Same answer",
            deck=deck1
        )
        card2 = Card.objects.create(
            question="Duplicate question?",
            answer="Same answer",
            deck=deck2
        )
        
        assert card1.question == card2.question
        assert card1.answer == card2.answer
        assert card1.deck != card2.deck


@pytest.mark.django_db
class TestCardWithReviewHistory:
    """Test Card relationships with ReviewHistory"""
    
    def test_card_review_history_cascade_delete(self, user, card):
        """Test that deleting a card deletes related review history"""
        review1 = ReviewHistory.objects.create(
            user=user,
            card=card,
            quality=4
        )
        review2 = ReviewHistory.objects.create(
            user=user,
            card=card,
            quality=5
        )
        
        review_ids = [review1.id, review2.id]
        
        card.delete()
        
        assert not ReviewHistory.objects.filter(id__in=review_ids).exists()

    def test_card_review_history_related_name(self, user, card):
        """Test accessing reviews through card's related_name"""
        review1 = ReviewHistory.objects.create(user=user, card=card, quality=4)
        review2 = ReviewHistory.objects.create(user=user, card=card, quality=5)
        
        assert card.review_history.count() == 2
        assert review1 in card.review_history.all()
        assert review2 in card.review_history.all()


@pytest.mark.django_db
class TestCardWithProgress:
    """Test Card relationships with CardProgress"""
    
    def test_card_progress_cascade_delete(self, user, card):
        """Test that deleting a card deletes related progress"""
        
        from django.contrib.auth import get_user_model

        User = get_user_model()

        another_user = User.objects.create_user(
            username="anotheruser",
            email="another@example.com",
            password="testpass123"
        )

        progress1 = CardProgress.objects.create(
            user=user,
            card=card,
            repetitions=3
        )
        progress2 = CardProgress.objects.create(
            user=another_user,  # Different user
            card=card,
            repetitions=2
        ) if user else None
        
        progress_ids = [progress1.id]
        if progress2:
            progress_ids.append(progress2.id)
        
        card.delete()
        
        assert not CardProgress.objects.filter(id__in=progress_ids).exists()

    def test_card_progress_related_name(self, user, card):
        """Test accessing progress through card's related_name"""
        progress = CardProgress.objects.create(
            user=user,
            card=card,
            repetitions=5
        )
        
        assert card.card_progress.count() >= 1
        assert progress in card.card_progress.all()


@pytest.mark.django_db
class TestCardOrdering:
    """Test Card queryset ordering"""
    
    def test_card_ordering_by_created_at(self, deck):
        """Test that cards are ordered by created_at"""
        import time
        
        card1 = Card.objects.create(
            question="First?",
            answer="First answer",
            deck=deck
        )
        time.sleep(0.1)
        card2 = Card.objects.create(
            question="Second?",
            answer="Second answer",
            deck=deck
        )
        time.sleep(0.1)
        card3 = Card.objects.create(
            question="Third?",
            answer="Third answer",
            deck=deck
        )
        
        cards = Card.objects.filter(deck=deck)
        
        # Check order by creation (should be in order created)
        assert cards[0].id == card1.id
        assert cards[1].id == card2.id
        assert cards[2].id == card3.id


@pytest.mark.django_db
class TestCardQueries:
    """Test Card queryset operations"""
    
    def test_card_filter_by_deck(self, deck):
        """Test filtering cards by deck"""
        card1 = Card.objects.create(question="Q1?", answer="A1", deck=deck)
        card2 = Card.objects.create(question="Q2?", answer="A2", deck=deck)
        
        filtered = Card.objects.filter(deck=deck)
        
        assert filtered.count() == 2
        assert card1 in filtered
        assert card2 in filtered

    def test_card_filter_by_question(self, deck):
        """Test filtering cards by question content"""
        card1 = Card.objects.create(
            question="Python question?",
            answer="Python answer",
            deck=deck
        )
        card2 = Card.objects.create(
            question="JavaScript question?",
            answer="JS answer",
            deck=deck
        )
        
        python_cards = Card.objects.filter(question__contains="Python")
        
        assert python_cards.count() == 1
        assert card1 in python_cards
        assert card2 not in python_cards

    def test_card_count_in_deck(self, multiple_decks):
        """Test counting cards in different decks"""
        deck1, deck2, deck3 = multiple_decks
        
        # Add cards to different decks
        for i in range(3):
            Card.objects.create(question=f"Q{i}?", answer=f"A{i}", deck=deck1)
        
        for i in range(2):
            Card.objects.create(question=f"Q{i}?", answer=f"A{i}", deck=deck2)
        
        Card.objects.create(question="Q?", answer="A", deck=deck3)
        
        assert deck1.cards.count() == 3
        assert deck2.cards.count() == 2
        assert deck3.cards.count() == 1

    def test_card_get_or_create(self, deck):
        """Test get_or_create for cards"""
        card1, created1 = Card.objects.get_or_create(
            question="Unique question?",
            defaults={"answer": "Answer", "deck": deck}
        )
        
        assert created1 is True
        
        card2, created2 = Card.objects.get_or_create(
            question="Unique question?",
            defaults={"answer": "Answer", "deck": deck}
        )
        
        assert created2 is False
        assert card1.id == card2.id


@pytest.mark.django_db
class TestCardEdgeCases:
    """Test edge cases and special scenarios"""
    
    def test_card_with_html_in_question_answer(self, deck):
        """Test that HTML content is stored as-is"""
        card = Card.objects.create(
            question="<b>What is HTML?</b>",
            answer="<i>Markup language</i>",
            deck=deck
        )
        
        assert "<b>What is HTML?</b>" in card.question
        assert "<i>Markup language</i>" in card.answer

    def test_card_with_unicode_characters(self, deck):
        """Test card with unicode characters"""
        card = Card.objects.create(
            question="¿Qué es Python? 你好",
            answer="Ελληνικά αλφάβητο",
            deck=deck
        )
        
        assert "¿Qué es" in card.question
        assert "你好" in card.question
        assert "Ελληνικά" in card.answer

    def test_card_with_newlines_and_formatting(self, deck):
        """Test card with multiline text"""
        multiline_question = "Question line 1\nQuestion line 2\nQuestion line 3"
        multiline_answer = "Answer\n\nWith\n\nMultiple\nLines"
        
        card = Card.objects.create(
            question=multiline_question,
            answer=multiline_answer,
            deck=deck
        )
        
        assert "\n" in card.question
        assert "\n" in card.answer
        assert card.question.count("\n") == 2
        assert card.answer.count("\n") == 5

    def test_card_with_special_characters_and_punctuation(self, deck):
        """Test card with special characters"""
        card = Card.objects.create(
            question='What is !@#$%^&*()_+-={}[]|:;"<>,.?/?',
            answer='!@#$%^&*()@[]{}<>?',
            deck=deck
        )
        
        assert card.question == 'What is !@#$%^&*()_+-={}[]|:;"<>,.?/?'
        assert card.answer == '!@#$%^&*()@[]{}<>?'

    def test_card_modification(self, deck):
        """Test modifying card fields"""
        card = Card.objects.create(
            question="Original question?",
            answer="Original answer",
            deck=deck
        )
        
        original_created_at = card.created_at
        
        card.question = "Modified question?"
        card.answer = "Modified answer"
        card.save()
        
        fetched_card = Card.objects.get(id=card.id)
        
        assert fetched_card.question == "Modified question?"
        assert fetched_card.answer == "Modified answer"
        assert fetched_card.created_at == original_created_at
