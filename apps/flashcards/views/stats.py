from .base import * 




from ..serializers.stats import UserStatsSerializer,DeckStatsSerializer



class UserStatsView(APIView):
    """
    Return user-level learning statistis across all decks.
    Includes total cards,reviews done today
    ,due cards, and more.
    """
    permission_classes = [IsAuthenticated]
  


    @swagger_auto_schema(
            tags=["FlashCard-Stats"],
            operation_description="Get the user-level learning statistis",
            responses={
                200: openapi.Response(
                    'Success: Ok',
                    UserStatsSerializer
                ),
                400: 'Error: Bad request',
                429: 'Error: Too many requests',
                500: 'Error: Internal server error'
            }
            
    )

    def get(self,request):
        try:
            now = timezone.now()
            today_start = now.replace(hour = 0,minute = 0,second=0,microsecond=0)
            today_end = today_start + timedelta(days=1)

            # total decks  & cards 

            total_decks = Deck.objects.filter(user=request.user).count()
            total_cards = Card.objects.filter(deck__user=request.user).count()

            # -- reviews due today (SM-2) --
            due_today = CardProgress.objects.filter(
                user = request.user,
                next_review_date__range = [today_start,today_end]
            ).count()

            # -- overdue reviews -- 

            overdue = CardProgress.objects.filter(
                user = request.user,
                next_review_date__lt = today_start
            ).count()

            reviews_due_today = due_today + overdue



            #  -- reviews completed today -- 

            reviews_today = ReviewHistory.objects.filter(
                user = request.user,
                reviewed_at__range = [today_start,today_end]
            ).count()


            # -- known vs unkown  ratios -- 
            known_count = ReviewHistory.objects.filter(user=request.user, known = True).count()
            unkown_count = ReviewHistory.objects.filter(user= request.user, known = False).count()


            data = {

                "total_decks":total_decks,
                "total_cards":total_cards,
                "reviews_due_today":reviews_due_today,
                "due_today":due_today,
                "overdue":overdue,
                "reviews_done_today":reviews_today,
                "known_cards":known_count,
                "unknown_cards":unkown_count,
                "completion_rate":(
                    (known_count / total_cards) * 100 if total_cards > 0 else 0
                ),
            }
            
            serializer = UserStatsSerializer(data)
            return Response(serializer.data,status=status.HTTP_200_OK)
        
        except Exception as e:
           
           logger.error(f"Error in DeckReviewSuggestionView.get():{str(e)}",
                        exc_info=True
                        )
           return Response(
              {"detail":str(e)},
              status=status.HTTP_404_NOT_FOUND
           )

class DeckStatsView(APIView):

    """
    Return statistics for a specific deck:

    - total cards
    - due for review 
    - reviews done today 
    - known vs unkown 
    
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
            tags=["FlashCard-Stats"],
            operation_description="Get the deck level user learning statistis",
            responses={
                200: openapi.Response(
                    'Success: Ok',
                    DeckStatsSerializer
                ),
                400: 'Error: Bad request',
                429: 'Error: Too many requests',
                500: 'Error: Internal server error'
            }
            
    )

    def get(self, request, deck_id):

        try:
            now = timezone.now()
            today_start = now.replace(hour=0,minute=0,second=0,microsecond=0)
            today_end = today_start + timedelta(days=1)

            deck = Deck.objects.get(id=deck_id,user = request.user)

            cards = Card.objects.filter(deck=deck)

            # Reviews (history) for this deck
            reviews = ReviewHistory.objects.filter(user=request.user,card__deck = deck)

            
            total_cards = cards.count()

          
                        # -- reviews due today (SM-2) --
            due_today = CardProgress.objects.filter(
                user = request.user,
                next_review_date__range = [today_start,today_end]
            ).count()

            # -- overdue reviews -- 

            overdue = CardProgress.objects.filter(
                user = request.user,
                next_review_date__lt = today_start
            ).count()

            reviews_due_today = due_today + overdue

            # Reviews done today
            reviews_today = reviews.filter(reviewed_at__range=[today_start,today_end]).count()


            known_count = reviews.filter(known=True).count()
            unknown_count = reviews.filter(known=False).count()


            
            data = {
                "deck_name": deck.name,
                "total_cards": total_cards,
                "reviews_due_today":reviews_due_today,
                "due_today":due_today,
                "overdue":overdue,
                "reviews_done_today": reviews_today,
                "known_cards": known_count,
                "unknown_cards": unknown_count,
                "completion_rate": (
                    (known_count / total_cards) * 100 if total_cards > 0 else 0
                ),
            }
            
            serializer = DeckStatsSerializer(data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Deck.DoesNotExist:
            return Response(
                {"detail": "Deck not found or not owned by user."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
           
           logger.error(f"Error in DeckStatsView.get():{str(e)}",
                        exc_info=True
                        )
           return Response(
              {"detail":str(e)},
              status=status.HTTP_404_NOT_FOUND
           )
