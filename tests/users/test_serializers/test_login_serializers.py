import pytest 

from rest_framework.exceptions import ValidationError 

from apps.users.serializers import (
    LoginSerializer,
    LoginResponseSerializer
)

@pytest.mark.django_db
class TestLoginSerializers:

    def test_login_serializer_valid_data(self,user):

        data = {

            'username':'testuser',
            'password':'testpass123'
        }

        serializer = LoginSerializer(data=data, context={'request':None})

        assert serializer.is_valid()
        assert serializer.validated_data['user'] == user
    
    def test_login_serializer_invalid_credentials(self):

        data = {
            'username':'testuser',
            'password':'wrongpassword'
        }

        serializer = LoginSerializer(data=data, context = {'request':None})

        assert not serializer.is_valid()
        with pytest.raises(ValidationError):

            serializer.is_valid(raise_exception=True)

    def test_login_serializer_missing_fields(self):

        data = {

            'username':'testuser'
        }

        serializer = LoginSerializer(data=data , context={'request':None})

        assert not serializer.is_valid()

        with pytest.raises(ValidationError):

            serializer.is_valid(raise_exception=True)

    def test_login_response_serializer(self,user):
        # Create the response data 
        response_data = {

            'refresh':'refresh_token',
            'access':'access_token',
            'user':user
        }

        # Test the serializer 
        serializer = LoginResponseSerializer(response_data)

        #Verify the data 

        serailized_data = serializer.data 


        assert serailized_data['refresh'] == response_data['refresh']
        
        assert serailized_data['access'] == response_data['access']

        assert serailized_data['user']['id'] == user.id

        assert serailized_data['user']['username'] == user.username 

        assert serailized_data['user']['mastered_cards'] == user.mastered_cards

        assert serailized_data['user']['cards_reviewed'] == user.cards_reviewed

        