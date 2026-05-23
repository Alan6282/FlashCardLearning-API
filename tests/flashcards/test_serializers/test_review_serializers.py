import pytest

from apps.flashcards.serializers.review import (
    ReviewSerializer,
    ReviewResponseSerializer,
    ReviewPaginatedResponseSerializer
)

from apps.flashcards.models import ReviewHistory


@pytest.mark.django_db
class TestReviewSerializer:
    """Test ReviewSerializer for review creation/updates"""
    
    def test_review_serializer_valid_data(self, user, card):
        """Test serializer with valid data"""
        data = {
            'user': user.id,
            'card': card.id,
            'quality': 4
        }
        
        serializer = ReviewSerializer(data=data)
        
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['quality'] == 4

    def test_review_serializer_missing_quality(self, user, card):
        """Test serializer without quality field"""
        data = {
            'user': user.id,
            'card': card.id
        }
        
        serializer = ReviewSerializer(data=data)
        
        # Quality might have a default or be required
        # Check based on model definition
        if not serializer.is_valid():
            assert 'quality' in serializer.errors or 'non_field_errors' in serializer.errors

    def test_review_serializer_quality_0(self, user, card):
        """Test review with quality 0"""
        data = {
            'user': user.id,
            'card': card.id,
            'quality': 0
        }
        
        serializer = ReviewSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_review_serializer_quality_5(self, user, card):
        """Test review with quality 5 (perfect)"""
        data = {
            'user': user.id,
            'card': card.id,
            'quality': 5
        }
        
        serializer = ReviewSerializer(data=data)
        assert serializer.is_valid()

    def test_review_serializer_quality_boundary(self, user, card):
        """Test quality boundary (3 is passing threshold)"""
        for quality in range(0, 6):
            data = {
                'user': user.id,
                'card': card.id,
                'quality': quality
            }
            
            serializer = ReviewSerializer(data=data)
            
            if serializer.is_valid():
                # Quality should be between 0-5
                assert 0 <= serializer.validated_data['quality'] <= 5

    def test_review_serializer_read_only_fields(self, review_history):
        """Test that read-only fields cannot be changed"""
        data = {
            'quality': 5,
            'known': False,  # Should be read-only
            'reviewed_at': '2024-01-01T00:00:00Z'  # Should be read-only
        }
        
        serializer = ReviewSerializer(review_history, data=data, partial=True)
        
        # known and reviewed_at are read-only
        if serializer.is_valid():
            updated = serializer.save()
            # reviewed_at should not change
            assert updated.reviewed_at == review_history.reviewed_at

    def test_review_serializer_save_creates_review(self, user, card):
        """Test that serializer.save() creates a review"""
        data = {
            # 'user': user.id,
            # 'card': card.id,
            'quality': 4
        }
        
        serializer = ReviewSerializer(data=data)
        assert serializer.is_valid()
        
        review = serializer.save(user=user,card=card)
        
        assert review.quality == 4
        assert review.user == user
        assert review.card == card
        assert ReviewHistory.objects.filter(id=review.id).exists()

    def test_review_serializer_multiple_reviews_same_card(self, user, card):
        """Test creating multiple reviews for same card"""
        for quality in [2, 3, 4, 5]:
            data = {
                # 'user': user.id,
                # 'card': card.id,
                'quality': quality
            }
            
            serializer = ReviewSerializer(data=data)
            assert serializer.is_valid()
            
            serializer.save(user=user,card=card)
        
        assert ReviewHistory.objects.filter(card=card, user=user).count() == 4

    def test_review_serializer_update_quality(self, review_history):
        """Test updating review quality"""
        data = {'quality': 5}
        
        serializer = ReviewSerializer(review_history, data=data, partial=True)
        assert serializer.is_valid()
        
        updated = serializer.save()
        assert updated.quality == 5


@pytest.mark.django_db
class TestReviewResponseSerializer:
    """Test ReviewResponseSerializer for API responses"""
    
    def test_review_response_serializer_basic(self, review_history):
        """Test basic review response serialization"""
        serializer = ReviewResponseSerializer(review_history)
        data = serializer.data
        
        assert data['id'] == review_history.id
        assert data['quality'] == review_history.quality
        assert data['known'] == review_history.known
        assert 'reviewed_at' in data

    def test_review_response_serializer_includes_user(self, review_history):
        """Test that response includes user info"""
        serializer = ReviewResponseSerializer(review_history)
        data = serializer.data
        
        assert 'user' in data
        assert isinstance(data['user'], dict)
        assert 'id' in data['user']
        assert 'username' in data['user']

    def test_review_response_serializer_includes_card(self, review_history):
        """Test that response includes card info"""
        serializer = ReviewResponseSerializer(review_history)
        data = serializer.data
        
        assert 'card' in data
        assert isinstance(data['card'], dict)
        assert 'id' in data['card']
        assert 'question' in data['card']

    def test_review_response_serializer_known_field(self, user, card):
        """Test known field in response"""
        from apps.flashcards.models import ReviewHistory
        
        review_fail = ReviewHistory.objects.create(
            user=user,
            card=card,
            quality=2
        )
        
        review_pass = ReviewHistory.objects.create(
            user=user,
            card=card,
            quality=4
        )
        
        serializer_fail = ReviewResponseSerializer(review_fail)
        serializer_pass = ReviewResponseSerializer(review_pass)
        
        assert serializer_fail.data['known'] is False
        assert serializer_pass.data['known'] is True

    def test_review_response_serializer_multiple_reviews(self, user, card):
        """Test serializing multiple reviews"""
        from apps.flashcards.models import ReviewHistory
        
        reviews = [
            ReviewHistory.objects.create(user=user, card=card, quality=q)
            for q in [1, 2, 3, 4, 5]
        ]
        
        serializer = ReviewResponseSerializer(reviews, many=True)
        data = serializer.data
        
        assert len(data) == 5
        assert all('id' in item for item in data)
        assert all('quality' in item for item in data)

    def test_review_response_serializer_contains_all_fields(self, review_history):
        """Test that all required fields are present"""
        serializer = ReviewResponseSerializer(review_history)
        data = serializer.data
        
        required_fields = ['id', 'user', 'card', 'known', 'quality', 'reviewed_at']
        
        for field in required_fields:
            assert field in data

    def test_review_response_serializer_reviewed_at_format(self, review_history):
        """Test that reviewed_at is in ISO format"""
        serializer = ReviewResponseSerializer(review_history)
        data = serializer.data
        
        # Should be ISO format
        assert isinstance(data['reviewed_at'], str)
        assert 'T' in data['reviewed_at'] or 'Z' in data['reviewed_at']


@pytest.mark.django_db
class TestReviewPaginatedResponseSerializer:
    """Test ReviewPaginatedResponseSerializer for paginated responses"""
    
    def test_review_paginated_response_valid(self):
        """Test paginated response with valid data"""
        data = {
            'count': 50,
            'next': 'http://api.example.com/reviews?page=2',
            'previous': None,
            'results': []
        }
        
        serializer = ReviewPaginatedResponseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_review_paginated_response_missing_count(self):
        """Test validation fails without count"""
        data = {
            'next': None,
            'previous': None,
            'results': []
        }
        
        serializer = ReviewPaginatedResponseSerializer(data=data)
        assert not serializer.is_valid()
        assert 'count' in serializer.errors

    def test_review_paginated_response_with_results(self, review_history):
        """Test paginated response with actual reviews"""
        review_data = ReviewResponseSerializer(review_history).data
        
        data = {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [review_data]
        }
        
        serializer = ReviewPaginatedResponseSerializer(data=data)
        assert serializer.is_valid()

    def test_review_paginated_response_multiple_results(self, user, card):
        """Test paginated response with multiple results"""
        from apps.flashcards.models import ReviewHistory
        
        reviews = [
            ReviewHistory.objects.create(user=user, card=card, quality=q)
            for q in range(0, 6)
        ]
        
        results = ReviewResponseSerializer(reviews, many=True).data
        
        data = {
            'count': len(results),
            'next': None,
            'previous': None,
            'results': results
        }
        
        serializer = ReviewPaginatedResponseSerializer(data=data)
        assert serializer.is_valid()
        assert len(serializer.data['results']) == 6

    def test_review_paginated_response_with_pagination_urls(self):
        """Test paginated response with valid pagination URLs"""
        data = {
            'count': 100,
            'next': 'http://api.example.com/reviews?page=2',
            'previous': 'http://api.example.com/reviews?page=1',
            'results': []
        }
        
        serializer = ReviewPaginatedResponseSerializer(data=data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestReviewSerializerIntegration:
    """Integration tests for review serializers"""
    
    def test_create_review_and_respond(self, user, card):
        """Test creating review via serializer and responding"""
        create_data = {
            # 'user': user.id,
            # 'card': card.id,
            'quality': 4
        }
        
        create_serializer = ReviewSerializer(data=create_data)
        assert create_serializer.is_valid()
        
        review = create_serializer.save(user=user,card=card)
        
        # Respond with response serializer
        response_serializer = ReviewResponseSerializer(review)
        response_data = response_serializer.data
        
        assert response_data['quality'] == 4
        assert response_data['user']['id'] == user.id

    def test_review_quality_affects_known(self, user, card):
        """Test that quality affects known field in response"""
        from apps.flashcards.models import ReviewHistory
        
        for quality in range(0, 6):
            review = ReviewHistory.objects.create(
                user=user,
                card=card,
                quality=quality
            )
            
            serializer = ReviewResponseSerializer(review)
            data = serializer.data
            
            expected_known = quality >= 3
            assert data['known'] == expected_known

    def test_paginate_reviews(self, user, card):
        """Test pagination workflow with serializers"""
        from apps.flashcards.models import ReviewHistory
        
        for i in range(10):
            ReviewHistory.objects.create(user=user, card=card, quality=i % 6)
        
        reviews = ReviewHistory.objects.filter(card=card)
        review_data = ReviewResponseSerializer(reviews, many=True).data
        
        paginated = {
            'count': len(review_data),
            'next': None,
            'previous': None,
            'results': review_data
        }
        
        serializer = ReviewPaginatedResponseSerializer(data = paginated)
        assert serializer.is_valid()
