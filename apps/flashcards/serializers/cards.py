from rest_framework import serializers 
from ..models import Card
from .decks import DeckResponseSerializer

class CardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Card
        fields = '__all__'
        read_only_fields = ['deck']

    
class CardResponseSerializer(serializers.ModelSerializer):

    deck = DeckResponseSerializer(read_only=True)


    class Meta:
        model = Card
        fields = ['id','deck','question','answer','created_at']
    
class CardPaginatedResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        help_text = "Total number of cards"
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
        help_text = "List of cards",
        many=True
    )

    