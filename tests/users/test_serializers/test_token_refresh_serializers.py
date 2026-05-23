import pytest

from apps.users.serializers import TokenRefreshResponseSerializer

@pytest.mark.django_db
class TestTokenRefreshSerializers:
    def test_token_refresh_response_serializer(self):

        data = {
            'refresh':'new_refresh_token'
        }

        serializer = TokenRefreshResponseSerializer(data=data)
        assert serializer.is_valid()

        # Verify the data 

        serialized_data = serializer.data 
        assert serialized_data['refresh'] == data['refresh']
        assert 'access' in serializer.fields # Check if field exists in serializer 
        assert serializer.fields['access'].read_only # Verify it's read-only 

    


