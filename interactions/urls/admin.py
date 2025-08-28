from django.urls import path
from interactions.views.admin import *

urlpatterns = [
    # Admin request management URLs
    path('requests/', admin_request_list_view, name='admin_request_list'),
    path('requests/<int:request_id>/', admin_request_detail_view, name='admin_request_detail'),
    path('requests/<int:request_id>/mark-processed/', admin_mark_processed_view, name='admin_mark_processed'),
]
