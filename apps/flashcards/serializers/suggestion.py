
from .base import *
from rest_framework import  serializers
from ..models import CardProgress
from ..serializers.cards import CardResponseSerializer


class CardProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardProgress
        fields = ["user", "card", "repetitions", "interval", "ease_factor", "next_review_date"]
        read_only_fields = ["repetitions", "interval", "ease_factor", "next_review_date"]


class CardProgressResponseSerializer(serializers.ModelSerializer):

    class Meta:

        model = CardProgress
        fields = ["card","next_review_date"]




class SuggestionPaginatedResponseSerializer(serializers.Serializer):

    count = serializers.IntegerField(
        help_text = "Total number of due cards"
    )
    next = serializers.URLField(
        help_text = "URL for next page(null if no more pages)",
        allow_null=True
    )
    previous = serializers.URLField(
        help_text="URL for previous page (null if first page)",
        allow_null =True
    )

    results = CardResponseSerializer(
        help_text = "List of cards due for review",
        many=True
    )
    