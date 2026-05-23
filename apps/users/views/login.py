from ..serializers.login import LoginResponseSerializer,LoginSerializer
from .base import *

class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [HighLimitAnonRateThrottle]
    #set throttle 

    @swagger_auto_schema(
          
          tags=["Authentication"],
          operation_id="user login",
          operation_description="Login user & get JWT tokens",
          request_body=LoginSerializer,
          responses={
             200: openapi.Response(
                'Success: Ok',
               LoginResponseSerializer
             ),
             400: 'Error: Bad request',
             429: 'Error: Too many requests',
             500: 'Error: Internal server error',
          }

    )

    def post(self,request):
        

     try:
        serializer=LoginSerializer(data=request.data,context={'request':request})



        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # JWT TOKEN GENERATION
        refresh = RefreshToken.for_user(user)

        response = {
           'user':user,
           'access':str(refresh.access_token),
           'refresh':str(refresh)
        }

        return Response(LoginResponseSerializer(response).data,status=status.HTTP_200_OK)


     except ValidationError as e:
        
        return Response(
           
         {"detail":str(e)},  
        status=status.HTTP_400_BAD_REQUEST
           
        )
     except Exception as e:
        #log the error for debugging 
        logger.error(
           f"Error in LoginView.post():{str(e)}",
           exc_info=True
        )

        return Response(
           {"detail":"An error occured while processing your request."},
           status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )