import pytest 

from apps.users.serializers import LogoutSerializer

@pytest.mark.django_db
class TestLogoutSerializers:
    def test_logout_serailizer_valid_data(self):

        data = {

            'refresh':'refresh_token'
        }
        serailizer = LogoutSerializer(data=data)
        assert serailizer.is_valid()
        assert serailizer.data == data 

    def test_logout_serializer_missing_refresh(self):
    
        data = {}
        serializer = LogoutSerializer(data=data)
        assert not serializer.is_valid()
        assert 'refresh' in serializer.errors

