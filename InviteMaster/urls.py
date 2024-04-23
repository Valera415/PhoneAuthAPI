from django.urls import path

from .views import *


urlpatterns = [
    path('', home, name='home'),
    path('logout/', user_logout, name='logout'),
    path('verify_phone/', verify_phone, name='verify_phone'),
    path('profile/', profile, name='profile'),

    path('api/authorize/', UserAuthorization.as_view(), name='user_authorization'),
    path('api/referral_code/', UserReferralCode.as_view(), name='user_referral_code'),
    path('api/generate_code/', GenerateAuthorizationCode.as_view(), name='generate_code'),
]