from django.urls import path
from .. import views

urlpatterns = [
    path('load-chunks/<int:chapter_id>/', views.load_more_chunks, name='load_more_chunks'),
    path('save-progress/', views.save_reading_progress, name='save_reading_progress'),
]
