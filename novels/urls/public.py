from django.urls import path
from novels.views.public import *

urlpatterns = [
    path("", Home, name="home"),
    path("most-read/", most_read_novels, name="most_read_novels"),
    path("new/", new_novels, name="new_novels"),
    path("finished/", finish_novels, name="finish_novels"),
    path("create/", NovelCreateView.as_view(), name="novel_create"),
    path("my-novels/", MyNovelsView.as_view(), name="my_novels"),
    path('upload-rules/novel/', novel_upload_rules, name='novel_upload_rules'),
    path('upload-rules/chapter/', chapter_upload_rules, name='chapter_upload_rules'),
    path('search/', search_novels, name='search_novels'),
    
    # Novel and chapter routes
    path('<slug:novel_slug>/', novel_detail, name='novel_detail'),
    path('<slug:novel_slug>/chapters/', chapter_list_view, name='chapter_list'),
    path('<slug:novel_slug>/add-chapter/', chapter_add_view, name='chapter_add'),
    path('<slug:novel_slug>/chapter/<slug:chapter_slug>/', chapter_detail_view, name='chapter_detail'),
    path('<slug:novel_slug>/chapter/<slug:chapter_slug>/delete/', chapter_delete_view, name='chapter_delete'),
]
