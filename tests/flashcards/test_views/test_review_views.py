import pytest
from django.urls import reverse
from rest_framework import status

from apps.flashcards.models import Card, Deck, ReviewHistory


@pytest.mark.django_db
class TestReviewListView:
    """Test Review List API endpoint (GET /reviews/)"""

    def test_get_reviews_unauthenticated(self, client):
        """Test that unauthenticated request is rejected"""
        url = reverse('review_list')
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_reviews_authenticated_empty(self, user_client):
        """Test authenticated user gets empty list when no reviews exist"""
        url = reverse('review_list')
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert response.data['count'] == 0

    def test_get_reviews_returns_only_own_reviews(self, user_client, user, card):
        """Test user only sees their own reviews, not other users'"""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        ReviewHistory.objects.create(user=user, card=card, quality=4)

        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        ReviewHistory.objects.create(user=other_user, card=card, quality=3)

        url = reverse('review_list')
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_get_reviews_pagination(self, user_client, user, card):
        """Test that review list is paginated"""
        for i in range(25):
            ReviewHistory.objects.create(user=user, card=card, quality=i % 6)

        url = reverse('review_list')
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data

    def test_get_reviews_custom_page_size(self, user_client, user, card):
        """Test custom page size query param"""
        for i in range(10):
            ReviewHistory.objects.create(user=user, card=card, quality=i % 6)

        url = reverse('review_list')
        response = user_client.get(f'{url}?page_size=5')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) <= 5

    def test_get_reviews_filter_by_card(self, user_client, user, deck):
        """Test filtering reviews by card ID"""
        card1 = Card.objects.create(deck=deck, question='Q1?', answer='A1')
        card2 = Card.objects.create(deck=deck, question='Q2?', answer='A2')

        ReviewHistory.objects.create(user=user, card=card1, quality=4)
        ReviewHistory.objects.create(user=user, card=card2, quality=2)

        url = reverse('review_list')
        response = user_client.get(f'{url}?card={card1.id}')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['card']['id'] == card1.id

    def test_get_reviews_filter_by_known_true(self, user_client, user, card):
        """Test filtering reviews where known=True (quality >= 3)"""
        ReviewHistory.objects.create(user=user, card=card, quality=4)  # known
        ReviewHistory.objects.create(user=user, card=card, quality=1)  # unknown

        url = reverse('review_list')
        response = user_client.get(f'{url}?known=True')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['known'] is True

    def test_get_reviews_filter_by_known_false(self, user_client, user, card):
        """Test filtering reviews where known=False (quality < 3)"""
        ReviewHistory.objects.create(user=user, card=card, quality=4)  # known
        ReviewHistory.objects.create(user=user, card=card, quality=1)  # unknown

        url = reverse('review_list')
        response = user_client.get(f'{url}?known=False')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['known'] is False

    def test_get_reviews_ordering_default(self, user_client, user, card):
        """Test default ordering is by reviewed_at descending"""
        r1 = ReviewHistory.objects.create(user=user, card=card, quality=3)
        r2 = ReviewHistory.objects.create(user=user, card=card, quality=4)

        url = reverse('review_list')
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert results[0]['id'] == r2.id  # most recent first

    def test_get_reviews_ordering_by_reviewed_at_asc(self, user_client, user, card):
        """Test ordering by reviewed_at ascending"""
        r1 = ReviewHistory.objects.create(user=user, card=card, quality=3)
        r2 = ReviewHistory.objects.create(user=user, card=card, quality=4)

        url = reverse('review_list')
        response = user_client.get(f'{url}?ordering=reviewed_at')

        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert results[0]['id'] == r1.id  # oldest first

    def test_get_reviews_response_format(self, user_client, user, card):
        """Test response includes all required fields"""
        ReviewHistory.objects.create(user=user, card=card, quality=4)

        url = reverse('review_list')
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data

        result = response.data['results'][0]
        assert 'id' in result['card']
        assert 'card' in result
        assert 'known' in result
        assert 'reviewed_at' in result

    def test_get_reviews_caching(self, user_client, user, card):
        """Test that repeated requests use cache and return consistent data"""
        ReviewHistory.objects.create(user=user, card=card, quality=4)

        url = reverse('review_list')
        response1 = user_client.get(url)
        response2 = user_client.get(url)

        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        assert response1.data == response2.data


@pytest.mark.django_db
class TestReviewDetailView:
    """Test Review Detail API endpoint (GET /reviews/<review_id>/)"""

    def test_get_review_detail_unauthenticated(self, client, user, card):
        """Test that unauthenticated request is rejected"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=4)

        url = reverse('review_detail', kwargs={'review_id': review.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_review_detail_authenticated(self, user_client, user, card):
        """Test authenticated user can get their review by ID"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=4)

        url = reverse('review_detail', kwargs={'review_id': review.id})
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == review.id
        assert response.data['known'] is True

    def test_get_review_detail_nonexistent(self, user_client):
        """Test getting a non-existent review returns 404"""
        url = reverse('review_detail', kwargs={'review_id': 9999})
        response = user_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_review_detail_other_user(self, user_client, card):
        """Test user cannot access another user's review"""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        review = ReviewHistory.objects.create(user=other_user, card=card, quality=4)

        url = reverse('review_detail', kwargs={'review_id': review.id})
        response = user_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_review_detail_response_format(self, user_client, user, card):
        """Test review detail response includes all expected fields"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=3)

        url = reverse('review_detail', kwargs={'review_id': review.id})
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert 'id' in response.data
        assert 'card' in response.data
        assert 'known' in response.data
        assert 'reviewed_at' in response.data

    def test_get_review_detail_known_true_for_high_quality(self, user_client, user, card):
        """Test known=True for quality >= 3"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=5)

        url = reverse('review_detail', kwargs={'review_id': review.id})
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['known'] is True

    def test_get_review_detail_known_false_for_low_quality(self, user_client, user, card):
        """Test known=False for quality < 3"""
        review = ReviewHistory.objects.create(user=user, card=card, quality=2)

        url = reverse('review_detail', kwargs={'review_id': review.id})
        response = user_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['known'] is False