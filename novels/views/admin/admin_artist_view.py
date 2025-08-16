from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from novels.models import Artist
from novels.forms import ArtistForm
from common.decorators import website_admin_required
from constants import (
    PAGINATOR_COMMON_LIST,
    PAGINATION_PAGE_RANGE,
)

@website_admin_required
def artist_list(request):
    search_query = request.GET.get('q', '')
    artists = Artist.objects.all().order_by('name')
    if search_query:
        artists = artists.filter(name__icontains=search_query) | artists.filter(pen_name__icontains=search_query)

    paginator = Paginator(artists, PAGINATOR_COMMON_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "title": _("Quản lý Họa sĩ"),
        "item_name": _("họa sĩ"),
        "table_partial": "admin/author_artist/partials/list_table_artist.html",
        "list_url": reverse('novels:artist_list'),
        "create_url": reverse('novels:artist_create'),
        "js_path": "admin/js/crud_common.js",
        "page_obj": page_obj,
        "search_query": search_query,
        "PAGINATION_PAGE_RANGE": PAGINATION_PAGE_RANGE,
    }

    return render(request, "admin/author_artist/list_common.html", context)

@website_admin_required
def artist_create(request):
    if request.method == 'POST':
        form = ArtistForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return render(request, 'admin/author_artist/partials/form.html', {'form': ArtistForm()})

@website_admin_required
def artist_update(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    if request.method == 'POST':
        form = ArtistForm(request.POST, instance=artist)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return render(request, 'admin/author_artist/partials/form.html', {'form': ArtistForm(instance=artist)})

@website_admin_required
def artist_delete(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    artist.delete()
    return JsonResponse({'success': True})
