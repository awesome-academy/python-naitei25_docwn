from django.urls import path, include

app_name = 'interactions'

urlpatterns = [
    path('', include('interactions.urls.public')),
    path("ajax/", include('interactions.urls.ajax')),
    path("admin/", include('interactions.urls.admin')),
]
