from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError,NotFound
from rest_framework import filters

# importing the serializers 
from ..serializers.cards import CardSerializer,CardResponseSerializer,CardPaginatedResponseSerializer
from ..serializers.review import ReviewSerializer,ReviewResponseSerializer,ReviewPaginatedResponseSerializer
from ..serializers.decks import DeckSerializer,DeckResponseSerializer,DeckPaginatedResponseSerializer
from ..serializers.stats import UserStatsSerializer,DeckStatsSerializer
from ..serializers.suggestion import SuggestionPaginatedResponseSerializer

# importing the models 
from ..models import Card,ReviewHistory,Deck,CardProgress

# importing the paginators 
from ..paginators import CardListPagination,ReviewListPagination,DeckListPagination


from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# importing the swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi 

from django.db import IntegrityError,transaction
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta


from django.views.decorators.vary import vary_on_headers
from django.core.cache import cache

import logging

# Create Logger Instance 
logger = logging.getLogger(__name__)
