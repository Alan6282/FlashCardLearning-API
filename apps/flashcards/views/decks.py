from .base import *


# Helper function for user cache invalidation
def invalidate_user_cache(user_id: int, key_type: str = "deck_list"):
    """Invalidate Redis cache for a specific user and key type."""
    cache.delete_pattern(f"*user_{user_id}_{key_type}_*")


CACHE_TIMEOUT = 60 * 15

class DeckListCreateView(APIView):

    permission_classes = [IsAuthenticated]
    pagination_class = DeckListPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    

    '''
    Get the All Decks Owned By The User
    '''

    @swagger_auto_schema(
          tags=["FlashCard-Decks"],
          operation_description="Get/retrieve all decks",
          manual_parameters=[
             openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Page number (default: 1)",
                type=openapi.TYPE_INTEGER,
                required=False
             ),
             openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description=(
                   f"Number of results per page (default: {DeckListPagination.page_size}, "
                   f"max: {DeckListPagination.max_page_size})"
                ),
                type=openapi.TYPE_INTEGER,
                required=False
             ),
             openapi.Parameter(
             'category',
              openapi.IN_QUERY,
              description="Filter deck by category ",
              type=openapi.TYPE_STRING,
              required=False
            ),
           openapi.Parameter(
               'is_public',
               openapi.IN_QUERY,
               description="Filter by visibility status (true/false)",
               type=openapi.TYPE_BOOLEAN,
               required=False
            ),
           openapi.Parameter(
               'search',
               openapi.IN_QUERY,
               description="Search decks by name or description",
               type=openapi.TYPE_STRING,
               required=False
            ),
           openapi.Parameter(
               'ordering',
               openapi.IN_QUERY,
               description="Order results by field (e.g., 'created_at' or 'name')",
               type=openapi.TYPE_STRING,
               required=False
            ),
          ],
          responses={
             200: openapi.Response(
                'Success: Ok',
                DeckPaginatedResponseSerializer
             ),
            400: 'Error: Bad Request',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
          }


    )
   
    @method_decorator(vary_on_headers('Authorization'))
    def get(self,request):
      try:
        user_id = request.user.id

        # setting the cache key 
        cache_key = f"user_{user_id}_deck_list"  

       
        #getting the cached data , if cache exists
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        

        decks = Deck.objects.filter(user=request.user)

        for backend_class in list(self.filter_backends):
           backend = backend_class()
           decks = backend.filter_queryset(self.request,decks,self)

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(decks,request)

        if result_page is not None:
           serializer = DeckResponseSerializer(result_page,many=True) 
           paginated_response = paginator.get_paginated_response(serializer.data)
           response_data = paginated_response.data   


           # setting the cached data 

           cache.set(cache_key, response_data, CACHE_TIMEOUT)

           return Response(response_data)

        
        return Response({"detail":"Pagination is required for this endpoint "},status=status.HTTP_400_BAD_REQUEST)
      
   
      
      except NotFound as e:

         return Response(
           {"detail": {str(e)}},
            status=status.HTTP_404_NOT_FOUND 
         )
      except Exception as e:

         # log the error for debugging 
         logger.error(
            f"Error in DeckListCreateView.get():{str(e)}",
            exc_info=True
         )

         return Response(
            {"detail":"An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
         )
    
    '''
    Create A Deck for the User
    '''

    @swagger_auto_schema(
          tags=["FlashCard-Decks"],
          operation_description="Create a new Deck",
          request_body=DeckSerializer,
          responses={
             201: openapi.Response(
                'Success: Created',
                DeckSerializer
             ),
             400: 'Error: Bad request',
             401: 'Error: Unauthorized',
             403: 'Error: Forbidden',
             429: 'Error: Too many requests',
             500: 'Error: Internal server error'
          }
    )
    def post(self,request):

      try:
      
         serializer = DeckSerializer(data=request.data)

         if serializer.is_valid():
            deck=serializer.save(user=request.user)
            invalidate_user_cache(request.user.id)
            
            return Response(DeckResponseSerializer(deck).data,status=status.HTTP_201_CREATED)
         
         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
      
      except ValidationError as e:
         return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
         )
      except IntegrityError as e:
      
         return Response(
            {"detail":  str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
      except Exception as e:
         #log the error for debugging 
         logger.error(
            f"Error in DeckListCreateView.post(): {str(e)}",
            exc_info=True
         )
         return Response(
            {"detail":"An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
         )
     
class DeckDetailView(APIView):
   
   permission_classes = [IsAuthenticated]


   '''
   Get a Specific Deck Owned by the User
   '''

   @swagger_auto_schema(
         tags=["FlashCard-Decks"],
         operation_description="Get/retrieve a Deck by ID",
         manual_parameters=[
            openapi.Parameter(
               'deck_id',
               openapi.IN_PATH,
               description="ID of the deck to retrieve",
               type=openapi.TYPE_INTEGER,
               required=True
            ),
         ],
         responses={
            200: openapi.Response(
               'Success: Ok',
               DeckSerializer
            ),
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        
         }

   )
   def get(self,request,deck_id):
      
      try:
         
         deck = Deck.objects.get(id=deck_id ,user = request.user)
         return Response(DeckResponseSerializer(deck).data,status=status.HTTP_200_OK)
         
      except Deck.DoesNotExist:
         
         return Response(
            {"detail":"Deck Not Found"},status=status.HTTP_404_NOT_FOUND

         )
      except NotFound as e:

         return Response(
            {"detail":str(e)},
            status=status.HTTP_404_NOT_FOUND)
      except Exception as e:

         # log the error for debugging
         logger.error(
            f"Error in DeckDetailView.get(): {str(e)}",
            exc_info=True
         )

         return Response(
            {"detail":"An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
         )   
   '''
   Updating a Deck by ID using put method
   
   '''
   @swagger_auto_schema(
         tags=["FlashCard-Decks"],
         operation_description="Update a deck by ID using PUT method",
         manual_parameters=[
            openapi.Parameter(
               'deck_id',
               openapi.IN_PATH,
               description="ID of the Deck to update",
               type=openapi.TYPE_INTEGER,
               required=True
            ),
         ],

         request_body=DeckSerializer,
         responses={
            200: openapi.Response(
               'Success: Ok',
               DeckSerializer
            ),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
            
         }
   )
   
   def put(self,request,deck_id):
      
     try:

        deck = Deck.objects.get(id=deck_id,user = request.user)

        serializer = DeckSerializer(deck, data = request.data)

        serializer.is_valid(raise_exception=True)

        deck = serializer.save()

        invalidate_user_cache(request.user.id)

        return Response(
           DeckResponseSerializer(deck).data,
           status=status.HTTP_200_OK
        )
     


     except Deck.DoesNotExist:

        return Response(
          {"detail":"Deck not Found."},status=status.HTTP_404_NOT_FOUND
        )
     

     except ValidationError as e:
         return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST
         )
     except IntegrityError as e:
      
         return Response(
            {"detail":  str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
     except Exception as e:

         # log the error for debugging
         logger.error(
            f"Error in DeckDetailView.put(): {str(e)}",
            exc_info=True
         )

         return Response(
            {"detail":"An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
         )  
     


   @swagger_auto_schema(
         tags=["FlashCard-Decks"],
         operation_description="Update a deck by ID using PATCH method",
         manual_parameters=[
            openapi.Parameter(
               'deck_id',
               openapi.IN_PATH,
               description="ID of the Deck to update",
               type=openapi.TYPE_INTEGER,
               required=True
            ),
         ],

         request_body=DeckSerializer,
         responses={
            200: openapi.Response(
               'Success: Ok',
               DeckSerializer
            ),
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
            
         }
   )
   
        
   
   def patch(self,request,deck_id):
      
      try:
         
         deck = Deck.objects.get(id=deck_id,user=request.user)

         serializer = DeckSerializer(deck,data=request.data,partial=True)

         serializer.is_valid(raise_exception=True)

         deck =serializer.save()

         invalidate_user_cache(request.user.id)

         return Response(
           DeckResponseSerializer(deck).data,
           status=status.HTTP_200_OK
        )


      except Deck.DoesNotExist:
         
          return Response(
          {"detail":"Deck not Found."},status=status.HTTP_404_NOT_FOUND
        )
      except ValidationError as e:

         return Response(
            {"detail":str(e)},
            status=status.HTTP_400_BAD_REQUEST
         )
      except IntegrityError as e:

         return Response(
            {"detail":str(e)},
            status=status.HTTP_400_BAD_REQUEST
         )
      except Exception as e:

         # log the error for debugging
         logger.error(
            f"Error in DeckDetailView.patch(): {str(e)}",
            exc_info=True
         )

         return Response(
            {"detail":"An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
         )  
        

   
   '''
   Deleting a Deck 
   
   '''

   @swagger_auto_schema(
         tags=["FlashCard-Decks"],
         operation_description="Delete a deck by ID ",
         manual_parameters=[
            openapi.Parameter(
               'deck_id',
               openapi.IN_PATH,
               description="ID of the Deck to delete",
               type=openapi.TYPE_INTEGER,
               required=True
            ),
         ],

         request_body=DeckSerializer,
         responses={
            204: 'Success: No content',
            400: 'Error: Bad Request',
            401: 'Error: Unauthorized',
            403: 'Error: Forbidden',
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
            
         }
   )
   def delete(self,request,deck_id):
      
      try:
         
         deck =Deck.objects.get(id=deck_id,user=request.user)

         deck.delete()

         #invalidating the cache
         invalidate_user_cache(request.user.id)

         return Response(status=status.HTTP_204_NO_CONTENT)
      
      except Deck.DoesNotExist:
         
         return Response(

            {"detail":"Deck not Found"},status=status.HTTP_404_NOT_FOUND
         )
      except Exception as e:

         # log the error for debugging
         logger.error(
            f"Error in DeckDetailView.delete(): {str(e)}",
            exc_info=True
         )

         return Response(
            {"detail":"An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
         )  
        