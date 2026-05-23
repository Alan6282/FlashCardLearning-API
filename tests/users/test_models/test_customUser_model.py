import pytest 
from django.core.exceptions import ValidationError
from apps.users.models import CustomUser


@pytest.mark.django_db
class TestCustomUser:

    def test_given_and_default_values(self,user):


        assert user.username == 'testuser'

        assert user.cards_reviewed == 0

        assert user.mastered_cards == 0 


        assert user.check_password('testpass123')

    def test_string_representation(self,user):

        assert str(user) == f"testuser (Mastered Cards:{user.mastered_cards})"

    def test_field_constraints(self,user):

        # Test mastered_cards score cannot be negative 


        with pytest.raises(ValidationError):

            user.mastered_cards = -1
            user.full_clean()
        
        # Test reviewed_cards cannot be negative 

        with pytest.raises(ValidationError):

            user.cards_reviewed = -1

            user.full_clean()

    def test_field_update(self,user):

        # Test by updating highest value on the fields
        user.mastered_cards = 100
        user.save()
        assert user.mastered_cards == 100

        user.cards_reviewed = 100
        user.save()
        assert user.cards_reviewed == 100

   


       




    def test_indexes(self):

        # verify indexes are created 

        indexes = CustomUser._meta.indexes
        index_names = [ index.name for index in indexes ]

        assert 'username_idx' in index_names
