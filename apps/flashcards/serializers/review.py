from rest_framework import serializers
from ..models import ReviewHistory
from ...users.serializers.userinfo import UserInfoSerializer
from .cards import CardSerializer

class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReviewHistory
        fields = '__all__'
        read_only_fields = ['user','card','known',"reviewed_at"]

class ReviewResponseSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer(read_only=True)
    card = CardSerializer(read_only=True)
    class Meta:
        model = ReviewHistory
        fields =['id','user','card','known','quality','reviewed_at']

class ReviewPaginatedResponseSerializer(serializers.Serializer):

    count = serializers.IntegerField(
        help_text = "Total number of review"
    )
    next = serializers.URLField(
        help_text = "URL for next page(null if no more pages)",
        allow_null=True
    )
    previous = serializers.URLField(
        help_text="URL for previous page (null if first page)",
        allow_null =True
    )

    results = ReviewResponseSerializer(
        help_text = "List of decks",
        many=True
    )
    
