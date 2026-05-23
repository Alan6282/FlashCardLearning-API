import pytest 

from django.urls import reverse 

from rest_framework import status 



@pytest.mark.django_db
class TestLogoutView:
    def test_logout_success(self, api_client, user):
        # First login to get tokens
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = api_client.post(login_url, login_data, format='json')
        
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']
        # Now test logout
        url = reverse('logout')

        # Authenticate the request using the access token obtained 
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        data = {
            'refresh': refresh_token
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.data['detail'] == 'Logout Successful.'

    def test_logout_invalid_token(self, api_client,user):
        # First login to get tokens
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = api_client.post(login_url, login_data, format='json')


        # getting the access token 
        access_token = login_response.data['access']


        # Now test logout
        url = reverse('logout')

        # Authenticate the request using the access token obtained 
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        data = {
            'refresh': 'invalid_token'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'token' in str(response.data['detail']).lower()

    def test_logout_missing_token(self, api_client,user):
        # First login to get tokens
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = api_client.post(login_url, login_data, format='json')
        # getting the access token 
        access_token = login_response.data['access']


        # Now test logout
        url = reverse('logout')

        # Authenticate the request using the access token obtained 
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")


        data = {}  # Missing refresh token
        
        response = api_client.post(url, data, format='json')

        
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'refresh' in str(response.data['detail']).lower()

    def test_logout_expired_token(self, api_client,user):
       # First login to get tokens
        login_url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = api_client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']
        # Now test logout
        url = reverse('logout')

        # Authenticate the request using the access token obtained 
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")


        data = {
            'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUdfzI1NiJ9.eyJ0b2tlfgbkjkll90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYxNjI0ODQwMCwianRpIjoiMjU5ZDM0YzYtYjM0Yy00YjM1LWE5ZDAtYjM0YzQyYjM0YzQyIiwidXNlcl9pZCI6MX0.expired_token_signature'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'token' in str(response.data['detail']).lower()
