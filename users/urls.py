from django.urls import path
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import UserRegistrationView, UserProfileView


urlpatterns = [
       path('register/', UserRegistrationView.as_view(
           authentication_classes=[]
       ), name='register'),

       path('token/', TokenObtainPairView.as_view(
           authentication_classes=[SessionAuthentication, BasicAuthentication]
       ), name='token_obtain_pair'),

       path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

       path('profile/<int:pk>/', UserProfileView.as_view(
           authentication_classes=[JWTAuthentication]
       ), name='user-profile'),
   ]
