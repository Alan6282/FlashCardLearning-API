from ..serializers.register import RegisterSerializer,RegisterResponseSerializer
from .base import *

class RegisterView(APIView):
    """
     An Endpoint  to Create  New User 
    """
     
    permission_classes = [AllowAny]

    throttle_classes = [RegisterLoginThrottle]
    # set throttle 

    # Register a new user
    @swagger_auto_schema(
          tags=["Authentication"],
          operation_id="user_register",
          operation_description="Register a new user & get JWT tokens",
          request_body=RegisterSerializer,
          responses={
             201: openapi.Response(
                'Success: Created',
                RegisterResponseSerializer
             ),
             400: 'Error: Bad request',
             429: 'Error: Too many requests',
             500: 'Error: Internal server error'
          }

    )
    def post(self,request):
     try:

        data = request.data

        serializer = RegisterSerializer(data=data)
        
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        # Generate JWT Tokens
        refresh = RefreshToken.for_user(user)


        response = {
                   

                    'id': user.id,
                    'username': user.username,
                    'refresh':str(refresh),
                    'access':str(refresh.access_token),
                    


                    }
        
        
        return Response(RegisterResponseSerializer(response).data,status=status.HTTP_201_CREATED)

     except ValidationError as e:

      return Response(
        e.detail,  
        status=status.HTTP_400_BAD_REQUEST
    )
     

     except Exception as e:
            logger.error(f"Error in RegisterView.post(): {str(e)}", exc_info=True)
            return Response(
                {"detail": "An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )