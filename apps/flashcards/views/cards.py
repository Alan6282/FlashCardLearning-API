from .base import *



# Helper function for user cache invalidation
def invalidate_user_cache(user_id: int, key_type: str = "card_list"):
    """Invalidate Redis cache for a specific user and key type."""
    cache.delete_pattern(f"*user_{user_id}_{key_type}*")

def invalidate_deck_user_cache(user_id: int , key_type: str = "decksuggestion_list",deck_id=None):

   cache.delete_pattern(f"*user_{user_id}_{key_type}_{deck_id}*")

CACHE_TIMEOUT = 60 * 15


class CardListCreateView(APIView):

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
    '''
    Getting All the Cards Owned by the User Within the Deck
    '''
    
    @swagger_auto_schema(
          tags=["FlashCard-Cards"],
          operation_id="deck_flashcard_list",
          operation_description="Get/retrieve all cards within a deck",
          manual_parameters=[
             openapi.Parameter(
                'deck_id',
                openapi.IN_PATH,
                description="ID of the subject to get lessons for",
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
               CardPaginatedResponseSerializer
             ),
             400: 'Error: Bad Request',
             404: 'Error: Not found',
             429: 'Error: Too many requests',
             500: 'Error: Internal server error'
          }
          
    )


    @method_decorator(vary_on_headers('Authorization'))
    def get(self,request,deck_id):
        try:
            
            user_id = request.user.id

            #setting the cache key
            cache_key = f"user_{user_id}_card_list"

            #getting the cached data , if cache exists
            cached_data = cache.get(cache_key)
            if cached_data:
               return Response(cached_data)
            

           
            deck = Deck.objects.get(id=deck_id,user=request.user)

            card =  Card.objects.filter(deck=deck)


            # Applying Filters/Search/Ordering 

            for backend_class in list(self.filter_backends):
               backend = backend_class()
               card = backend.filter_queryset(self.request,card,self)

            # Apply pagination            
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(card,request)

            if result_page is not None:
               serializer = CardSerializer(result_page,many=True)
               paginated_response = paginator.get_paginated_response(serializer.data)
               response_data = paginated_response.data

               #setting the cached data 

               cache.set(cache_key,response_data,CACHE_TIMEOUT)
               
               return Response(response_data)
            
            return Response({"detail":"Pagination is required for this endpoint"},
                            status=status.HTTP_400_BAD_REQUEST)
            

        except Deck.DoesNotExist:

            return Response({
                "details":"Deck Doesn't Exists"
            })
               
        except NotFound as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
           
           logger.error(f"Error in CardListCreateView.get():{str(e)}",
                        exc_info=True
                        )
           return Response(
              {"detail":str(e)},
              status=status.HTTP_404_NOT_FOUND
           )
        


    '''

    Creating Card For the Authenticated User Within the Deck

    '''

    
    @swagger_auto_schema(
       tags=["FlashCard-Cards"],
       operation_id="deck_flashcard_create",
       operation_description="Create a new flashcard within a deck",
       manual_parameters=[
          openapi.Parameter(
             'deck_id',
             openapi.IN_PATH,
             description="ID of the deck to create card for",
             type=openapi.TYPE_INTEGER,
             required=True
          ),
       ],
       request_body=CardSerializer,
       responses={
          201: openapi.Response(
             'Success:Created',
             CardResponseSerializer
          ),
          400: 'Error: Bad Request',
          401: 'Error: Unauthorized',
          403: 'Error: Forbidden',
          404: 'Error: Not found',
          429: 'Error: Too many requests',
          500: 'Error: Internal server error'
       }
    )

    def post(self,request,deck_id):
        try:

          deck = Deck.objects.get(id=deck_id,user=request.user)

          serializer = CardSerializer(data=request.data)

          serializer.is_valid(raise_exception=True)

          card = serializer.save(deck=deck)

          # invalidating the cache 
          invalidate_user_cache(request.user.id)

          return Response(CardResponseSerializer(card).data,status=status.HTTP_201_CREATED)
        
        except Deck.DoesNotExist:

            return Response({"details":"Deck Doesn't Exist"},
                            status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
           return Response(
              {"detail":str(e)},
              status=status.HTTP_400_BAD_REQUEST
           )
        except IntegrityError as e:
           return Response(
              {"detail":"Duplicate card title found within the same subject."},
              status=status.HTTP_400_BAD_REQUEST
           )
        except Exception as e:
           
           logger.error(
              f"Error in CardListCreateView.post(): {str(e)}",
              exc_info=True
           )
           return Response(
              {"detail":"An error occurred while processing your request."},
              status=status.HTTP_500_INTERNAL_SERVER_ERROR
   
           )
        





class CardReviewListCreateView(APIView):
   
   permission_classes = [IsAuthenticated]
   pagination_class = ReviewListPagination
   filter_backends = [
      DjangoFilterBackend,
      filters.OrderingFilter
   ]

   filterset_fields = ['known','reviewed_at']
   ordering_fields = ['reviewed_at']
   ordering = ['-reviewed_at']

   


   '''
   Getting All the review of a specific card by a user 
   '''
   @swagger_auto_schema(
         tags=["FlashCard-Reviews"],
         operation_id="card_review_list",
         operation_description="Get/retrieve all Reviews for a Card",
         manual_parameters=[
            openapi.Parameter(
               'card_id',
                openapi.IN_PATH,
                description="ID of the card to get reviews for",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
               'page',
               openapi.IN_QUERY,
               description="Page number (default:1)",
               type=openapi.TYPE_INTEGER,
               required=False
            ),
            openapi.Parameter(
               'page_size',
               openapi.IN_QUERY,
               description=(
                  f"Number of results per page(deault:{ReviewListPagination.page_size})",
                  f"max:{ReviewListPagination.max_page_size})"
               ),
               type=openapi.TYPE_INTEGER,
               required=False
            ),
            openapi.Parameter(
               'known',
               openapi.IN_QUERY,
               description="Filter cards by review status — set to `True` for cards answered correctly and `False` for cards answered incorrectly.",
               type=openapi.TYPE_BOOLEAN,
               required=False
            ),
            openapi.Parameter(
               'reviewed_at',
                openapi.IN_QUERY,
                description="Filter cards by review time",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
               'ordering',
               openapi.IN_QUERY,
               description="Order Cards by review time ",
               type=openapi.TYPE_STRING,
               required=False
            )
         ],
         responses={
            200: openapi.Response(
               'Success: Ok',
              ReviewPaginatedResponseSerializer
            ),
            400:'Error: Bad Request',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500:'Error: Internal server error'
         }

   )
   @method_decorator(cache_page(60*15,key_prefix=lambda request: f"user_{request.user.id}_card_review_list"))
   @method_decorator(vary_on_headers('Authorization'))

   def get(self,request, card_id):
      try: 
         user_id = request.user.id

         # setting the cache key 
         cache_key = f"user_{user_id}_card_review_list"

         #getting the cahed data , if cache exists 
         cached_data = cache.get(cache_key)
         if cached_data:
            return Response(cached_data)
         

         card = Card.objects.get(id=card_id)
         # filter can be global or per user
         review = ReviewHistory.objects.filter(user=request.user,card=card)


         for backend_class in list(self.filter_backends):
            backend =  backend_class()
            review = backend.filter_queryset(self.request,review,self)
         paginator = self.pagination_class()
         result_page = paginator.paginate_queryset(review,request)


         if result_page is not None:
            serializer = ReviewSerializer(result_page,many=True)
            paginated_response = paginator.get_paginated_response(serializer.data)
            response_data = paginated_response.data

            #setting the cached data 

            cache.set(cache_key,response_data,CACHE_TIMEOUT)

            
            return Response(response_data)
         
         return Response({"detail":"Pagination is required for this endpoint"}
                         ,status=status.HTTP_400_BAD_REQUEST)
      

         
      

      except Card.DoesNotExist:

         
         return Response({"detail":"Card doesn't exist"},
                         
                         status=status.HTTP_404_NOT_FOUND)
      

      except Exception as e:

         logger.error(
            f"Error in CardReviewListCreateView.get():{str(e)}",
            exc_info=True
         )
         return Response(

            {"detail":"An error occured while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
         )
      


   
 
   #Creating a Review for a card
   

   @swagger_auto_schema(
         tags=["FlashCard-Reviews"],
         operation_id="card_review_create",
         operation_description="Create a new review for a card.",
         manual_parameters=[
            openapi.Parameter(
               'card_id',
               openapi.IN_PATH,
               description="ID of the Card to create the review for",
               type=openapi.TYPE_INTEGER,
               required=True
            ),
         ],
         request_body=ReviewSerializer,
         responses={
            201: openapi.Response(
               'Success:Created',
               ReviewResponseSerializer
            ),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            403: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
         }

   )

   def post(self,request,card_id):  

      try:
         card = Card.objects.get(id=card_id)
      except Card.DoesNotExist:

         return Response(
            {"detail":"Card doesn't exist."},status=status.HTTP_404_NOT_FOUND
         )
      serializer = ReviewSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      quality = serializer.validated_data.get("quality")

      try:
         with transaction.atomic():

            # Append review into ReviewHistory
            review = ReviewHistory.objects.create(
               user=request.user,
               card = card,
               quality = int(quality)
            )

            # Update (or create) CardProgress and apply SM-2
            progress,_ = CardProgress.objects.get_or_create(user = request.user , card = card)
            progress.update_sm2(review.quality)

            # invalidate cache

            invalidate_user_cache(request.user.id,"suggestion_list")  # clears global suggestions
            invalidate_deck_user_cache(request.user.id, "decksuggestion_list", deck_id=card.deck.id) # clears deck specific suggestions

            
         return Response(ReviewResponseSerializer(review).data,status=status.HTTP_201_CREATED)
      

      except ValidationError as e:
          return Response(
             {"detail":str(e)},
             status=status.HTTP_400_BAD_REQUEST
          )
      
      except IntegrityError as e:
          return Response(
             {"detail":"Duplicate review  found for  the same card."},
             status=status.HTTP_400_BAD_REQUEST
          )
      except Exception as e:
          # log the error for debugging
          logger.error(
             f"Error in CardReviewListCreateView.post():{str(e)}",
             exc_info=True
          )

          return Response(
             {"detail":"An error occured while processing your request."},
             status=status.HTTP_500_INTERNAL_SERVER_ERROR
          )
       
    



class CardDetailView(APIView):
    

    permission_classes = [IsAuthenticated]



    #Getting A specific Card for the User


    @swagger_auto_schema(
          tags=["FlashCard-Cards"],
          operation_description="Get/retrieve a card by ID",
          manual_parameters=[
             openapi.Parameter(
                'card_id',
                openapi.IN_PATH,
                description="ID of the card to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True

             ),
          ],
          responses={
             200: openapi.Response(
                'Success: Ok',
                CardResponseSerializer
             ),
             404: 'Error: Not found',
             429: 'Error: Too many requests',
             500: 'Error: Internal server error'
          }
    )

    def get(self,request,card_id):
        
        try:
         

          card = Card.objects.get(id=card_id,deck__user=request.user)

          return Response(CardResponseSerializer(card).data,status=status.HTTP_200_OK)
        
        except Card.DoesNotExist:
           

            return Response(
               {"details":"Card Doesn't Exists."},
               status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
           #log the error for debugging
           logger.error(
              f"Error in CardDetailView.get():{str(e)}",
              exc_info=True
           )

           return Response(
              {"detail":"An error occurred while processing your request."},
              status=status.HTTP_500_INTERNAL_SERVER_ERROR
           )

    #update a 

    @swagger_auto_schema(
       tags=["FlashCard-Cards"],
       operation_description="Update a Card by ID using PUT method",
       manual_parameters=[
          openapi.Parameter(
                'card_id',
                openapi.IN_PATH,
                description="ID of the card to update",
                type=openapi.TYPE_INTEGER,
                required=True
          )
       
       ],
       request_body=CardSerializer,
       responses={
          200:openapi.Response(
             'Success: Ok',
             CardResponseSerializer
          ),
          400: 'Error: Bad Request',
          401: 'Error: Unauthorized',
          403: 'Error: Not found',
          429: 'Error: Too many requests',
          500: 'Error: Interna; server error'
       }
    )

    def put(self,request,card_id):
        try:
         

            card = Card.objects.get(id=card_id,deck__user=request.user)
            serializer = CardSerializer(card,data=request.data)

            serializer.is_valid(raise_exception=True)

            card =  serializer.save()

            #invalidating cache

            invalidate_user_cache(request.user.id)

            return Response(CardResponseSerializer(card).data,status=status.HTTP_200_OK)
        
        except Card.DoesNotExist:
           

            return Response(
               {"details":"Card Doesn't Exists."},
               status=status.HTTP_404_NOT_FOUND 
            )
        except ValidationError as e:
           return Response(
              {"detail":str(e)},
              status=status.HTTP_400_BAD_REQUEST
           )
        except IntegrityError as e:
           return Response (
              {"detail":"Duplicate Card title found within the same deck."},
              status=status.HTTP_400_BAD_REQUEST
           )
        

        except Exception as e:
           #log the error for debugging 
           logger.error(
              f"Error in CardDetailView.put():{str(e)}",
              exc_info=True
           )

           return Response(
              {"detail":"An error occured while processing your request."},
              status=status.HTTP_500_INTERNAL_SERVER_ERROR
           )
        

    #update a card by ID using PATCH method
    @swagger_auto_schema(
          tags=["FlashCard-Cards"],
          operation_description="Update a card by ID using PATCH method",
          manual_parameters=[
            openapi.Parameter(
                'card_id',
                openapi.IN_PATH,
                description="ID of the card to update",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
          ],
          request_body=CardSerializer,
          responses={
            200:openapi.Response(
               'Success: Ok',
               CardSerializer
            ),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not Found',
            429: 'Error: Too many requests',
            500: 'Error: Internal Server Error'
         }
    )


    def patch(self,request,card_id):
        try:
         

            card = Card.objects.get(id=card_id,deck__user=request.user)
            serializer = CardSerializer(card,data=request.data,partial=True)

            serializer.is_valid(raise_exception=True)

            card = serializer.save()

            #invalidate cache
            invalidate_user_cache(request.user.id)

            return Response(CardResponseSerializer(card).data,status=status.HTTP_200_OK)
         
        except Card.DoesNotExist:
           

            return Response(
                           {"details":"Card Doesn't Exists"},
                           status=status.HTTP_404_NOT_FOUND
            )
        
        except ValidationError as e:
           return Response(
              {"detail":str(e)},
              status=status.HTTP_400_BAD_REQUEST
           )
        
        except IntegrityError as e:
           return Response (
              {"detail":"Duplicate Card title found within the same deck."},
              status=status.HTTP_400_BAD_REQUEST
           )
        

        except Exception as e:
           #log the error for debugging 
           logger.error(
              f"Error in CardDetailView.patch():{str(e)}",
              exc_info=True
           )

           return Response(
              {"detail":"An error occured while processing your request."},
              status=status.HTTP_500_INTERNAL_SERVER_ERROR
           )
        

   #Delete a Card by ID
    @swagger_auto_schema(
      tags=["FlashCard-Cards"],
      operation_description="Delete a Card by ID",
      manual_parameters=[
         openapi.Parameter(
                'card_id',
                openapi.IN_PATH,
                description="ID of the card to delete",
                type=openapi.TYPE_INTEGER,
                required=True
         )
      ],
      responses={
            204: 'Success: No Content',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
      }
   )
    def delete(self,request,card_id):

      try:  
            card = Card.objects.get(id=card_id,deck__user=request.user)

            card.delete()

            #invalidate cache 

            invalidate_user_cache(request.user.id)

            return Response(status=status.HTTP_204_NO_CONTENT)

      
      except Card.DoesNotExist:
         
            return Response({"details":"Card Doesn't Exists."},
                           status=status.HTTP_404_NOT_FOUND
            )
      except Exception as e:
           #log the error for debugging 
           logger.error(
              f"Error in CardDetailView.delete():{str(e)}",
              exc_info=True
           )

           return Response(
              {"detail":"An error occured while processing your request."},
              status=status.HTTP_500_INTERNAL_SERVER_ERROR
           )
        