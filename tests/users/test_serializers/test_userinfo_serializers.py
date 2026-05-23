import pytest 

from apps.users.serializers import UserInfoSerializer

@pytest.mark.django_db
class TestUserInfoSerializer:

    def test_custom_user_serializer(self,user):

        serializer = UserInfoSerializer(user)
        data = serializer.data 

        assert data['id'] == user.id 
        assert data['username'] == user.username 
        assert data['mastered_cards'] == user.mastered_cards
        assert data['cards_reviewed'] == user.cards_reviewed


