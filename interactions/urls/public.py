from django.urls import path
from interactions.views.public import *

urlpatterns = [
    path('sse/stream/', sse_stream, name='sse_stream'),
    path('sse/ping/', sse_ping, name='sse_ping'),
    
    # Request URLs
    path('requests/submit/', submit_request_view, name='submit_request'),
    path('requests/my/', my_requests_view, name='my_requests'),
    path('requests/<int:request_id>/', request_detail_view, name='request_detail'),
]
