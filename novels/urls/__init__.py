from django.urls import path, include

app_name = 'novels'

urlpatterns = [
    path('', include('novels.urls.public')),
    path('ajax/', include('novels.urls.ajax')),
]
