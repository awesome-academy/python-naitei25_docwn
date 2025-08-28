"""
URL configuration for docwn project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog
from .settings import STATIC_ROOT, STATIC_URL, MEDIA_URL, MEDIA_ROOT

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("admin/", include("accounts.urls.admin")),
    path("admin/", include("novels.urls.admin")),
    path("admin/", include("interactions.urls.admin")),
    
    path("accounts/", include("accounts.urls")),
    path("novels/", include("novels.urls")),
    path("interactions/", include("interactions.urls")),
    path("tinymce/", include("tinymce.urls")),
    path("", RedirectView.as_view(url="novels/"), name='home'),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('i18n/', include('django.conf.urls.i18n')),
] + static(STATIC_URL, document_root=STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
