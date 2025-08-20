from django.urls import path
from novels.views.admin import *
app_name = "admin"
urlpatterns = [
    path("", Admin, name = "admin_home"),
    path("dashboard/", Dashboard, name="admin_dashboard"),
    path("novels/", Novels, name="admin_novels"),
    path("novels/<slug:slug>/", novel_detail, name="admin_novel_detail"),
    path("requests/novel/", upload_novel_requests, name="upload_novel_requests"),
    path("requests/novel/<slug:slug>/", novel_request_detail, name="novel_request_detail"),
    path("requests/novel/<slug:slug>/approve/", admin_approve_novel, name="admin_approve_novel"),
    path("requests/novel/<slug:slug>/reject/", admin_reject_novel, name="admin_reject_novel"),
    path("requests/chapter/", request_chapter_admin, name="upload_chapter_requests"),
    path("requests/chapter/<slug:chapter_slug>/", chapter_review, name="chapter_review"),
    path("requests/chapter/<slug:chapter_slug>/approve/", approve_chapter_view, name="approve_chapter"),
    path("requests/chapter/<slug:chapter_slug>/reject/", reject_chapter_view, name="reject_chapter"),
    
    # Author/Artist request management
    path("requests/author/", author_request_admin_list, name="author_request_list"),
    path("requests/author/<int:pk>/", author_request_admin_detail, name="author_request_detail"),
    path("requests/author/<int:pk>/approve/", approve_author_request, name="approve_author_request"),
    path("requests/author/<int:pk>/reject/", reject_author_request, name="reject_author_request"),
    path("requests/artist/", artist_request_admin_list, name="artist_request_list"),
    path("requests/artist/<int:pk>/", artist_request_admin_detail, name="artist_request_detail"),
    path("requests/artist/<int:pk>/approve/", approve_artist_request, name="approve_artist_request"),
    path("requests/artist/<int:pk>/reject/", reject_artist_request, name="reject_artist_request"),
    
    path("tags/", admin_tag_list, name="admin_tag_list"),
    path("tags/create/", admin_tag_create, name="admin_tag_create"),
    path("tags/<slug:tag_slug>/edit/", admin_tag_update, name="admin_tag_update"),
    path("tags/<slug:tag_slug>/delete/", admin_tag_delete, name="admin_tag_delete"),
    path("authors/", author_list, name="author_list"),
    path("authors/create/", author_create, name="author_create"),
    path("authors/<int:pk>/update/", author_update, name="author_update"),
    path("authors/<int:pk>/delete/", author_delete, name="author_delete"),
    path("artists/", artist_list, name="artist_list"),
    path("artists/create/", artist_create, name="artist_create"),
    path("artists/<int:pk>/update/", artist_update, name="artist_update"),
    path("artists/<int:pk>/delete/", artist_delete, name="artist_delete"),
]
