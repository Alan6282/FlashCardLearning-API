from .base import * 
from rest_framework import serializers

class UserStatsSerializer(serializers.Serializer):

    total_decks = serializers.IntegerField()
    total_cards = serializers.IntegerField()
    reviews_due_today = serializers.IntegerField()
    due_today = serializers.IntegerField()
    overdue = serializers.IntegerField()
    reviews_done_today = serializers.IntegerField()
    known_cards = serializers.IntegerField()
    unknown_cards = serializers.IntegerField()
    completion_rate = serializers.FloatField()


class DeckStatsSerializer(serializers.Serializer):
    deck_name = serializers.CharField()
    total_cards = serializers.IntegerField()
    reviews_due_today = serializers.IntegerField()
    due_today = serializers.IntegerField()
    overdue = serializers.IntegerField()
    reviews_done_today = serializers.IntegerField()
    known_cards = serializers.IntegerField()
    unknown_cards = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    