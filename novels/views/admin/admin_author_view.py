from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from novels.models import Author
from novels.forms import AuthorForm
from common.decorators import website_admin_required
from constants import (
    PAGINATOR_COMMON_LIST,
    PAGINATION_PAGE_RANGE,
)

@website_admin_required
def author_list(request):
    search_query = request.GET.get('q', '')
    authors = Author.objects.all().order_by('name')
    if search_query:
        authors = authors.filter(name__icontains=search_query) | authors.filter(pen_name__icontains=search_query)

    paginator = Paginator(authors, PAGINATOR_COMMON_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "title": _("Quản lý Tác giả"),
        "item_name": _("tác giả"),
        "table_partial": "admin/author_artist/partials/list_table_author.html",
        "list_url": reverse('novels:author_list'),
        "create_url": reverse('novels:author_create'),
        "js_path": "admin/js/crud_common.js",
        "page_obj": page_obj,
        "search_query": search_query,
        "PAGINATION_PAGE_RANGE": PAGINATION_PAGE_RANGE,
    }

    return render(request, "admin/author_artist/list_common.html", context)

@website_admin_required
def author_create(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return render(request, 'admin/author_artist/partials/form.html', {'form': AuthorForm()})

@website_admin_required
def author_update(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    return render(request, 'admin/author_artist/partials/form.html', {'form': AuthorForm(instance=author)})

@website_admin_required
def author_delete(request, pk):
    author = get_object_or_404(Author, pk=pk)
    author.delete()
    return JsonResponse({'success': True})
