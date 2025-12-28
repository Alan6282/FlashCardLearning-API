from .base import *
from ..serializers.logout import LogoutSerializer

class Logout(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [HighLimitAnonRateThrottle]
    # set up throttle 

    
    @swagger_auto_schema(
            tags=["Authentication"],
            operation_id="user_logout",
            operation_description="Logout user by refresh token",
            request_body=LogoutSerializer,
            responses={
                204:'Success: No Content',
                400: 'Error: Bad request',
                401: 'Error: Unauthorized',
                429: 'Error: Too many requests',
                500: 'Error: Internal server error'
            }
    )
    def post(self,request):

        try:
            serializer = LogoutSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            refresh_token = serializer.validated_data["refresh"]

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {
                    "Message":"Logout Successful."
                },status=status.HTTP_200_OK
            )
        except ValidationError as e:
         return Response(
            e.detail,  
            status=status.HTTP_400_BAD_REQUEST
         )


        except InvalidToken as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        except TokenError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

        except Exception as e:
            #log the error for debugging 

            logger.error(
                f"Error in LogoutView.post():{str(e)}",
                exc_info=True
            )

            return Response(

                {"detail":"An error occurred while processing your request."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        