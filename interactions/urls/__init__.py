from django.urls import path, include

app_name = 'interactions'

urlpatterns = [
    path('', include('interactions.urls.public')),
]
