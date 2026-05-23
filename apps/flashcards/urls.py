from django.urls import path
from .views.decks import DeckDetailView,DeckListCreateView
from .views.review import ReviewDetailView, ReviewListCreateView
from .views.cards import CardReviewListCreateView,CardListCreateView,CardDetailView
from .views.suggestion import ReviewSuggestionView,DeckReviewSuggestionView
from .views.stats import UserStatsView,DeckStatsView

urlpatterns = [
    
     # Deck Endpoints 
     path('decks/',DeckListCreateView.as_view(),name='deck_list_create'),
     path('decks/<int:deck_id>/',DeckDetailView.as_view(),name='deck_detail'),
     path("decks/<int:deck_id>/stats/",DeckStatsView.as_view(),name="deck_stats"),
     path("decks/<int:deck_id>/review/suggestions/",DeckReviewSuggestionView.as_view(), name="deck_review_suggestions"),

     #Card Endpoints 
     path('cards/<int:card_id>/reviews/', CardReviewListCreateView.as_view(), name='card_reviews'),
     path("decks/<int:deck_id>/cards/",CardListCreateView.as_view(),name="card_list_create"),
     path("cards/<int:card_id>/",CardDetailView.as_view(),name="card_detail"),

     #  Global review suggestions
     path("reviews-suggestions/",ReviewSuggestionView.as_view(),name="review_suggestions"),

     # stats 
     path("user/stats/",UserStatsView.as_view(),name="user_stats"),


     # Review Endpoints (GLOBAL)
     path('reviews/', ReviewListCreateView.as_view(), name='review_list'), 

    # Review   
     path('reviews/<int:review_id>/', ReviewDetailView.as_view(), name='review_detail'),
     
     

]


