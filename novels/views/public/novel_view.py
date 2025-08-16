from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import Http404

from novels.models import Novel
from novels.services import NovelService
from novels.forms import NovelForm
from constants import (
    ApprovalStatus, DATE_FORMAT_DMY, MAX_CHAPTER_LIST,
    MAX_CHAPTER_LIST_PLUS, DATE_FORMAT_DMYHI,
    MAX_TRUNCATED_REJECTED_REASON_LENGTH, PAGINATION_PAGE_RANGE,
    SUMMARY_TRUNCATE_WORDS, DEFAULT_RATING_AVERAGE
)
from common.decorators import require_active_novel

@require_active_novel
def novel_detail(request, novel_slug):
    """Novel detail page using service"""
    novel_data = NovelService.get_novel_detail(novel_slug, request.user)
    
    if not novel_data:
        return redirect("novels:home")
    
    context = {
        'is_owner': novel_data['is_owner'],
        'novel_slug': novel_slug,
        'novel': novel_data['novel'],
        'tags': novel_data['tags'],
        'volumes': novel_data['volumes'],
        'can_add_chapter': novel_data['can_add_chapter'],
        'DATE_FORMAT_DMY': DATE_FORMAT_DMY,
        'MAX_CHAPTER_LIST': MAX_CHAPTER_LIST,
        'MAX_CHAPTER_LIST_PLUS': MAX_CHAPTER_LIST_PLUS
    }
    return render(request, "novels/novel_detail.html", context)

class NovelCreateView(LoginRequiredMixin, CreateView):
    """Create new novel view"""
    model = Novel
    form_class = NovelForm
    template_name = "novels/novel_form.html"
    success_url = reverse_lazy("novels:home")
    login_url = reverse_lazy("accounts:login")
    permission_denied_message = _("Bạn cần đăng nhập để tạo tiểu thuyết mới.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Tạo tiểu thuyết mới")
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        save_as_draft = self.request.POST.get("save_as_draft", False)

        if save_as_draft:
            form.instance.approval_status = ApprovalStatus.DRAFT.value
        else:
            form.instance.approval_status = ApprovalStatus.PENDING.value

        upload_anonymously = form.cleaned_data.get("upload_anonymously", False)
        form.instance.is_anonymous = upload_anonymously
        form.instance.created_by = self.request.user if self.request.user.is_authenticated else None

        response = super().form_valid(form)

        # Handle ManyToMany tags relationship
        tags = form.cleaned_data.get("tags")
        if tags:
            self.object.tags.set(tags)

        return response

class MyNovelsView(LoginRequiredMixin, ListView):
    """User's novels management page using service"""
    template_name = "novels/my_novels.html"
    context_object_name = "page_obj"
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        status_filter = self.request.GET.get('status')
        page = self.request.GET.get('page', 1)
        return NovelService.get_user_novels_paginated(
            user=self.request.user,
            status_filter=status_filter,
            page=page
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Tiểu thuyết của tôi")
        context["DATE_FORMAT_DMY"] = DATE_FORMAT_DMY
        context["DATE_FORMAT_DMYHI"] = DATE_FORMAT_DMYHI
        
        # Get statistics using service
        stats = NovelService.get_user_novels_with_stats(self.request.user)
        context.update(stats)
        
        # Add status constants
        context.update({
            "DRAFT": ApprovalStatus.DRAFT.value,
            "PENDING": ApprovalStatus.PENDING.value,
            "APPROVED": ApprovalStatus.APPROVED.value,
            "REJECTED": ApprovalStatus.REJECTED.value,
            "MAX_TRUNCATED_REJECTED_REASON_LENGTH": MAX_TRUNCATED_REJECTED_REASON_LENGTH,
            "PAGINATION_PAGE_RANGE": PAGINATION_PAGE_RANGE,
            "current_filter": self.request.GET.get('status', 'all')
        })
        
        # Calculate pagination range
        if 'page_obj' in context and context['page_obj']:
            current_page = context['page_obj'].number
            context["pagination_start"] = current_page - PAGINATION_PAGE_RANGE
            context["pagination_end"] = current_page + PAGINATION_PAGE_RANGE
        
        return context

def novel_upload_rules(request):
    """Static page showing novel upload rules"""
    return render(request, 'novels/novel_upload_rule.html')

def search_novels(request):
    """Search novels using service"""
    query = request.GET.get('q', '').strip()
    novels = NovelService.search_novels(query) if query else []
    
    context = {
        'novels': novels,
        'query': query,
        'total_results': len(novels),
        'SUMMARY_TRUNCATE_WORDS': SUMMARY_TRUNCATE_WORDS,
        'DEFAULT_RATING_AVERAGE': DEFAULT_RATING_AVERAGE,
    }
    
    return render(request, 'novels/search_results.html', context)
