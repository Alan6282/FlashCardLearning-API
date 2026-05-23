from .base import *




class ReviewSuggestionView(APIView):

    """

    Suggests cards that are due for review today (across all decks)
    based on SM-2 next_review_date in CardProgress.

    
    """
    permission_classes = [IsAuthenticated]
    pagination_class = CardListPagination
    filter_backends = [
                       DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter
    ]
    filterset_fields = ['deck','created_at']

    search_fields = ['question']

    ordering_fields = ['created_at']

    ordering = ['-created_at']



    @swagger_auto_schema(
            tags=["FlashCard-Suggestions"],
            operation_description="Get due-review card suggestions (all decks)",

            manual_parameters=[
             openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description=(
                   f"Number of results per page (default:{CardListPagination.page_size})"
                   f"max: {CardListPagination.max_page_size}"
                ),
                type= openapi.TYPE_INTEGER,
                required= False
             ),
             openapi.Parameter(
                'deck',
                openapi.IN_QUERY,
                description="Filter cards based on deck",
                type=openapi.TYPE_STRING,
                required=False
             ),
             openapi.Parameter(
                'created_at',
                openapi.IN_QUERY,
                description="Filter cards based on creation time ",
                type=openapi.TYPE_STRING,
                required=False
             ),
             openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search Cards By question String",
                type=openapi.TYPE_STRING,
                required=False
             ),
             openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Order Cards Based on Creation time ",
                required=False
             )
  
         ],
            responses={
                200: openapi.Response(
                    'Success: Ok',
                    SuggestionPaginatedResponseSerializer
                    
                ),
                400: 'Error: Bad request',
                429: 'Error: Too many requests',
                500: 'Error: Internal server error'
            }
    )

    
    @method_decorator(vary_on_headers('Authorization'))

    def get(self,request):
         
         try:
                
                user_id = request.user.id

                params = request.GET.dict()

                sorted_params = "&".join(
                    f"{key}={value}"
                    for key, value in sorted(params.items())
                )

                # setting the cache key 
                cache_key = f"user_{user_id}_suggestion_list_{sorted_params}"

                # getting the cached data , if cache exists 
                cached_data = cache.get(cache_key)
                if cached_data:
                    return Response(cached_data)
        

                cards = Card.objects.filter(
                   card_progress__user=request.user,
                  card_progress__next_review_date__lte=timezone.now()
                )


                # Applying Filters/Search/Ordering

                for backend_class in list(self.filter_backends):
                   backend = backend_class()
                   cards= backend.filter_queryset(self.request,cards,self)

                   
                
                # Apply Pagination 
                paginator = self.pagination_class()
                result_page = paginator.paginate_queryset(cards,request)


                if result_page is not None: # Enforcing Pagination
                  serializer = CardResponseSerializer(result_page,many=True)
                 
                  paginated_response = paginator.get_paginated_response(serializer.data)

                  response_data = paginated_response.data

                  # setting the cached data 

                  cache.set(cache_key, response_data , CACHE_TIMEOUT)

                  return Response(response_data)
                

                # If pagination is not applied, throw an error
                return Response(
                   {"error": "Pagination is required for this endpoint."},
                   status=status.HTTP_400_BAD_REQUEST
                )
                
         
         except Exception as e:
           
           logger.error(f"Error in ReviewSuggestionView.get():{str(e)}",
                        exc_info=True
                        )
           return Response(
            {"detail":"An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
         )
        


class DeckReviewSuggestionView(APIView):

    """
    Returns cards from a specific deck* that are due for review today 
    according to the SM-2 spaced repetition schedule.
    """

    permission_classes = [IsAuthenticated]

    pagination_class = CardListPagination
    filter_backends = [
                       DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter
    ]
    filterset_fields = ['created_at']

    search_fields = ['question']

    ordering_fields = ['created_at']

    ordering = ['-created_at']

    @swagger_auto_schema(
            tags=["FlashCard-Suggestions"],
            operation_description="Get the due-review card suggestions based on the current deck",
            manual_parameters=[
             openapi.Parameter(
                'deck_id',
                openapi.IN_PATH,
                description="ID of the deck to get due cards for",
                type = openapi.TYPE_INTEGER,
                required=True
             ),
             openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description=(
                   f"Number of results per page (default:{CardListPagination.page_size})"
                   f"max: {CardListPagination.max_page_size}"
                ),
                type= openapi.TYPE_INTEGER,
                required= False
             ),
             openapi.Parameter(
                'deck',
                openapi.IN_QUERY,
                description="Filter cards based on deck",
                type=openapi.TYPE_STRING,
                required=False
             ),
             openapi.Parameter(
                'created_at',
                openapi.IN_QUERY,
                description="Filter cards based on creation time ",
                type=openapi.TYPE_STRING,
                required=False
             ),
             openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search Cards By question String",
                type=openapi.TYPE_STRING,
                required=False
             ),
             openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="Order Cards Based on Creation time ",
                required=False
             )
  
         ],
            responses={
                200: openapi.Response(
                    'Success: Ok',
                    SuggestionPaginatedResponseSerializer
                    
                ),
                400: 'Error: Bad request',
                429: 'Error: Too many requests',
                500: 'Error: Internal server error'
            }
    )

    
    @method_decorator(vary_on_headers('Authorization'))

    def get(self,request,deck_id): # deck id 

        try:
            
            user_id = request.user.id
           
            deck = Deck.objects.get(id=deck_id,user= request.user) # specific deck

            # setting the cache key 
            cache_key = f"user_{user_id}_decksuggestion_list_{deck.id}"

            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
            
            # Find the reviews for cards in this deck that are due for review
            
            cards = Card.objects.filter(
                   deck=deck, # specific deck
                   card_progress__user=request.user,
                   card_progress__next_review_date__lte=timezone.now()
                )


            # Applying Filters/Search/Ordering

            for backend_class in list(self.filter_backends):
                backend = backend_class()
                cards= backend.filter_queryset(self.request,cards,self)
            
            # Apply Pagination 
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(cards,request)

            if result_page is not None:
                serializer = CardResponseSerializer(result_page,many=True)
                paginated_response = paginator.get_paginated_response(serializer.data)
                
                # Extracting only the data for saving in the cache 
                response_data = paginated_response.data

                # setting the cached data 

                cache.set(cache_key, response_data , CACHE_TIMEOUT)

                return Response(response_data)
                
            
            return Response({"detail":"Pagination is required for this endpoint "},status=status.HTTP_400_BAD_REQUEST)

        except Deck.DoesNotExist:

            return Response(
                {"detail":"Deck not found "},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
           
           logger.error(f"Error in DeckReviewSuggestionView.get():{str(e)}",
                        exc_info=True
                        )
           return Response(
            {"detail":"An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
         )
        