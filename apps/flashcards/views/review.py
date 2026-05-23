from .base import *


# Helper function for user cache invalidation
def invalidate_user_cache(user_id: int, key_type: str = "review_list"):
    """Invalidate Redis cache for a specific user and key type."""

    if hasattr(cache,"delete_pattern"):
      
      cache.delete_pattern(f"*user_{user_id}_{key_type}*")



class ReviewListCreateView(APIView):

    permission_classes = [IsAuthenticated]
    pagination_class = ReviewListPagination
    filter_backends = [
      DjangoFilterBackend,
      filters.OrderingFilter
   ]

    filterset_fields = ['card', 'known','reviewed_at']
    ordering_fields = ['reviewed_at']
    ordering = ['-reviewed_at']

    '''
    Getting all the Reviews Made by the user
    '''
    
    @swagger_auto_schema(
          tags=["FlashCard-Reviews"],
          operation_description="Get/retrieve all reviews",
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
                   f"Number of results per page (default: {ReviewListPagination.page_size}, "
                   f"max: {ReviewListPagination.max_page_size})"
                   ),
               
                type = openapi.TYPE_INTEGER,
                required=False
               ), 
             openapi.Parameter(
               'card',
               openapi.IN_QUERY,
               description="Filter review by cards",
               type=openapi.TYPE_STRING,
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

      # Getting queries passed down to the endpoint through the request
      params = request.GET.dict()


      # sorted the queries to avoid duplicates by different orders of the queries

      sorted_params = "&".join(
           f"{key}={value}"
           for key, value in sorted(params.items())
      )


      # setting the cache key 
      cache_key = f"user_{user_id}_review_list_{sorted_params}"

      # getting the cached data , if cache exists 
      cached_data = cache.get(cache_key)
      if cached_data:
          return Response(cached_data)
      
      
      review = ReviewHistory.objects.filter(user=request.user)

 
     # Applying Filtering 

      for backend_class in list(self.filter_backends):
            backend = backend_class()
            review = backend.filter_queryset(self.request, review, self)


     # Applying Pagination

      paginator = self.pagination_class()
      result_page = paginator.paginate_queryset(review,request)

      if result_page is not None: # Enforcing Pagination
            serializer = ReviewResponseSerializer(result_page, many=True)
            paginated_response = paginator.get_paginated_response(serializer.data)
            response_data = paginated_response.data

            # setting the cached data 

            cache.set(cache_key, response_data , CACHE_TIMEOUT)

            return Response(response_data)

        #  if pagination is required and didn't apply
      return Response(
            {"error": "Pagination is required for this endpoint."},
            status=status.HTTP_400_BAD_REQUEST
        )

      
     
     except NotFound as e:
            
            return Response(
                {"details": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
     except Exception as e:

         # log the error for debugging 
         logger.error(
            f"Error in ReviewListCreateView.get():{str(e)}",
            exc_info=True
         )

         return Response(
            {"details":"An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
         )
    
          


class ReviewDetailView(APIView):


    permission_classes = [IsAuthenticated]


    '''
    Getting a Specific Review
    '''

    @swagger_auto_schema(
        tags=["FlashCard-Reviews"],
        operation_description="Get/retrieve a review by ID",
        manual_parameters=[
            openapi.Parameter(
                'review_id',
                openapi.IN_PATH,
                description="ID of the review to retrieve",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                'Success: Ok',
                ReviewSerializer
            ),
            404: 'Error: Not found',
            429: 'Error: Too many requests',
            500: 'Error: Internal server error'
        }
    )

    def get(self,request,review_id):
    
        try:
        
            review = ReviewHistory.objects.get(id=review_id,user = request.user)

            return Response(ReviewResponseSerializer(review).data,status=status.HTTP_200_OK)
        
        except ReviewHistory.DoesNotExist:
        
            return Response({"details":"Review Not Found"}, status=status.HTTP_404_NOT_FOUND)
               
        except Exception as e:

         # log the error for debugging 
         logger.error(
            f"Error in ReviewDetailView.get():{str(e)}",
            exc_info=True
         )

         return Response(
            {"details":"An error occurred while processing your request."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
         )
        

       

