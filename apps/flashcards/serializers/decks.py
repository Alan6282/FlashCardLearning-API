from rest_framework import serializers
from ..models import Deck
from ...users.serializers.userinfo import UserInfoSerializer 

class DeckSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Deck
        fields = '__all__'
        read_only_fields = ['user','share_link']
    
class DeckResponseSerializer(serializers.ModelSerializer):
     
    user = UserInfoSerializer(read_only=True)

    class Meta:
        model = Deck
        fields = ['id','name','category','description','created_at','user','is_public','share_link']

        def to_representation(self,instance):

            data = super().to_representation(instance)


            if not instance.is_public:
                data.pop("share_link",None)
            
            return data
class DeckPaginatedResponseSerializer(serializers.Serializer):

    count = serializers.IntegerField(
        help_text = "Total number of deck"
    )
    next = serializers.URLField(
        help_text = "URL for next page(null if no more pages)",
        allow_null=True
    )
    previous = serializers.URLField(
        help_text="URL for previous page (null if first page)",
        allow_null =True
    )

    results = DeckResponseSerializer(
        help_text = "List of decks",
        many=True
    )
    


        

    
