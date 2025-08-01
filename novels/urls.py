from django.urls import path
from django.http import HttpResponse
from . import views
from . import views_admin

app_name = 'novels'

urlpatterns = [
    path("", views.Home, name = "home"),
    path("admin/", views.Admin, name="admin"),
    path("create/", views.NovelCreateView.as_view(), name="novel_create"),
    path("admin/dashboard/", views.Dashboard, name="dashboard"),
    path("admin/users/", views.Users, name="users"),
    path("admin/novels/", views.Novels, name="novels"),
    path("admin/requests/", views.Requests, name="requests"),
    path("admin/comments/", views.Comments, name="comments"),
    path("my-novels/", views.MyNovelsView.as_view(), name="my_novels"),
    path('<slug:novel_slug>/', views.novel_detail, name='novel_detail'),
    path('novel/<slug:novel_slug>/chapter/<slug:chapter_slug>/', 
         views.chapter_detail_view, 
         name='chapter_detail'),
    path('ajax/load-chunks/<int:chapter_id>/', 
         views.load_more_chunks, 
         name='load_more_chunks'),
    
    path('ajax/save-progress/', 
         views.save_reading_progress, 
         name='save_reading_progress'),
    
    # Chapter list for a novel
    path('novel/<slug:novel_slug>/chapters/', 
         views.chapter_list_view, 
         name='chapter_list'),

     path('admin/', 
          views_admin.admin_dashboard, name='admin_dashboard'),

     path('admin/tags/', 
         views_admin.admin_tag_list, 
         name='admin_tag_list'),

     path('admin/tags/create/', 
          views_admin.admin_tag_create, 
          name='admin_tag_create'),

     path('admin/tags/<slug:tag_slug>/edit/', 
          views_admin.admin_tag_update, 
          name='admin_tag_update'),

     path('admin/tags/<slug:tag_slug>/delete/', 
          views_admin.admin_tag_delete, 
          name='admin_tag_delete'),
]
