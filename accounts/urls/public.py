from django.urls import path
from django.http import HttpResponse
from accounts.views.public import *

urlpatterns = [
    path("", lambda request: HttpResponse("Accounts Home")),
    # Authentication URLs
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Profile URLs
    path('profile/', profile_view, name='profile'),
    path('change-password/', change_password_view, name='change_password'),
    
    # Password Reset URLs
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('reset-password/<str:token>/', reset_password_view, name='reset_password'),
]
