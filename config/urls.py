from django.contrib import admin
from django.urls import path,include
from drf_yasg.views import get_schema_view 
from django.views.generic import RedirectView 
from drf_yasg import openapi  
from rest_framework import permissions

from config.swagger_schema import OrderedSchemaGenerator
  
schema_view = get_schema_view(  
   openapi.Info(  
      title="FlashCard Learning API",  
      default_version='v1',  
      description=(
          
            "API documentation for QuizLeader API\n"
            "GitHub Profile: https://github.com/Alan6282\n"
            "GitHub Repo (codes): https://github.com/Alan6282/Py-DRF__QuizLeader-API/"
      ),
      terms_of_service="https://www.google.com/policies/terms/",  
      contact=openapi.Contact(email="contact@yourapi.local"),  
      license=openapi.License(name="BSD License"), 
     
   ),  

   public=True,  
   permission_classes=(permissions.AllowAny,),  
   generator_class=OrderedSchemaGenerator, 
)  
  



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/swagger/', permanent=False), name='landing'), # landing page

    # config URLs for custom apps
    path('auth/',include('apps.users.urls')),
    path('flashcard/',include('apps.flashcards.urls')),


    # config URls for swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),  
]
