from django.urls import path
from .views.register import RegisterView
from .views.login import LoginView
from .views.logout import Logout
from .views.token_refresh import MyTokenRefreshView

urlpatterns = [
    path('register/',view=RegisterView.as_view(),name='register'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('login/',view=LoginView.as_view(),name='login'),
    path('logout/',view=Logout.as_view(),name='logout'), 
]
