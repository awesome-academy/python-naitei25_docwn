from django.db import transaction
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from novels.models import AuthorRequest, ArtistRequest, Author, Artist
from constants import ApprovalStatus, PAGINATOR_COMMON_LIST


class RequestService:
    @staticmethod
    def create_author_request(form_data, user):
        """Create a new author request"""
        author_request = AuthorRequest(
            name=form_data.get('name'),
            pen_name=form_data.get('pen_name'),
            description=form_data.get('description'),
            birthday=form_data.get('birthday'),
            deathday=form_data.get('deathday'),
            gender=form_data.get('gender'),
            country=form_data.get('country'),
            image_url=form_data.get('image_url'),
            created_by=user
        )
        author_request.save()
        return author_request

    @staticmethod
    def create_author_request_from_form(form, user):
        """Create a new author request from form"""
        author_request = form.save(commit=False)
        author_request.created_by = user
        author_request.save()
        return author_request

    @staticmethod
    def create_artist_request_from_form(form, user):
        """Create a new artist request from form"""
        artist_request = form.save(commit=False)
        artist_request.created_by = user
        artist_request.save()
        return artist_request

    @staticmethod
    def get_user_author_requests(user, page_number=None):
        """Get paginated author requests for a user"""
        requests = AuthorRequest.objects.filter(
            created_by=user
        ).order_by('-created_at')
        
        if page_number:
            paginator = Paginator(requests, PAGINATOR_COMMON_LIST)
            return paginator.get_page(page_number)
        return requests

    @staticmethod
    def get_user_artist_requests(user, page_number=None):
        """Get paginated artist requests for a user"""
        requests = ArtistRequest.objects.filter(
            created_by=user
        ).order_by('-created_at')
        
        if page_number:
            paginator = Paginator(requests, PAGINATOR_COMMON_LIST)
            return paginator.get_page(page_number)
        return requests

    @staticmethod
    def get_user_author_request(pk, user):
        """Get author request for specific user"""
        return get_object_or_404(AuthorRequest, pk=pk, created_by=user)

    @staticmethod
    def get_user_artist_request(pk, user):
        """Get artist request for specific user"""
        return get_object_or_404(ArtistRequest, pk=pk, created_by=user)


class AdminRequestService:
    @staticmethod
    def get_all_author_requests(status_filter=None, page_number=None, search_query=None, creator=None):
        """Get all author requests with optional filtering and search"""
        requests = AuthorRequest.objects.all()
        if status_filter:
            requests = requests.filter(approval_status=status_filter)
        if search_query:
            requests = requests.filter(
                name__icontains=search_query
            ) | requests.filter(
                pen_name__icontains=search_query
            )
        if creator:
            requests = requests.filter(created_by__username__icontains=creator)
        requests = requests.order_by('-created_at')
        if page_number:
            paginator = Paginator(requests, PAGINATOR_COMMON_LIST)
            return paginator.get_page(page_number)
        return requests

    @staticmethod
    def get_all_artist_requests(status_filter=None, page_number=None, search_query=None, creator=None):
        """Get all artist requests with optional filtering and search"""
        requests = ArtistRequest.objects.all()
        if status_filter:
            requests = requests.filter(approval_status=status_filter)
        if search_query:
            requests = requests.filter(
                name__icontains=search_query
            ) | requests.filter(
                pen_name__icontains=search_query
            )
        if creator:
            requests = requests.filter(created_by__username__icontains=creator)
        requests = requests.order_by('-created_at')
        if page_number:
            paginator = Paginator(requests, PAGINATOR_COMMON_LIST)
            return paginator.get_page(page_number)
        return requests

    @staticmethod
    def get_author_request(pk):
        """Get author request by ID"""
        return get_object_or_404(AuthorRequest, pk=pk)

    @staticmethod
    def get_artist_request(pk):
        """Get artist request by ID"""
        return get_object_or_404(ArtistRequest, pk=pk)

    @staticmethod
    def approve_author_request(pk, approved_by):
        """Approve an author request and create author"""
        author_request = get_object_or_404(AuthorRequest, pk=pk)
        
        if author_request.approval_status == ApprovalStatus.APPROVED.value:
            return {'success': False, 'message': _('Yêu cầu đã được duyệt trước đó.')}
        
        try:
            with transaction.atomic():
                # Check if author with same name already exists
                existing_author = Author.objects.filter(name=author_request.name).first()
                
                if existing_author:
                    # Use existing author instead of creating new one
                    author = existing_author
                    message = _('Tác giả "%(name)s" đã tồn tại. Đã sử dụng tác giả có sẵn.') % {'name': author_request.name}
                else:
                    # Create the author
                    author = Author.objects.create(
                        name=author_request.name,
                        pen_name=author_request.pen_name,
                        description=author_request.description,
                        birthday=author_request.birthday,
                        deathday=author_request.deathday,
                        gender=author_request.gender,
                        country=author_request.country,
                        image_url=author_request.image_url,
                    )
                    message = _('Yêu cầu thêm tác giả đã được duyệt thành công!')
                
                # Update the request
                author_request.approval_status = ApprovalStatus.APPROVED.value
                author_request.approved_by = approved_by
                author_request.created_author = author
                author_request.save()
                
                # Update novels that were using this request
                novels_to_update = author_request.novels.all()
                for novel in novels_to_update:
                    novel.author = author
                    novel.pending_author_request = None
                    novel.save()
                
                return {'success': True, 'message': message}
                
        except Exception as e:
            return {'success': False, 'message': _('Có lỗi xảy ra khi duyệt yêu cầu.')}

    @staticmethod
    def approve_artist_request(pk, approved_by):
        """Approve an artist request and create artist"""
        artist_request = get_object_or_404(ArtistRequest, pk=pk)
        
        if artist_request.approval_status == ApprovalStatus.APPROVED.value:
            return {'success': False, 'message': _('Yêu cầu đã được duyệt trước đó.')}
        
        try:
            with transaction.atomic():
                # Check if artist with same name already exists
                existing_artist = Artist.objects.filter(name=artist_request.name).first()
                
                if existing_artist:
                    # Use existing artist instead of creating new one
                    artist = existing_artist
                    message = _('Họa sĩ "%(name)s" đã tồn tại. Đã sử dụng họa sĩ có sẵn.') % {'name': artist_request.name}
                else:
                    # Create the artist
                    artist = Artist.objects.create(
                        name=artist_request.name,
                        pen_name=artist_request.pen_name,
                        description=artist_request.description,
                        birthday=artist_request.birthday,
                        deathday=artist_request.deathday,
                        gender=artist_request.gender,
                        country=artist_request.country,
                        image_url=artist_request.image_url,
                    )
                    message = _('Yêu cầu thêm họa sĩ đã được duyệt thành công!')
                
                # Update the request
                artist_request.approval_status = ApprovalStatus.APPROVED.value
                artist_request.approved_by = approved_by
                artist_request.created_artist = artist
                artist_request.save()
                
                # Update novels that were using this request
                novels_to_update = artist_request.novels.all()
                for novel in novels_to_update:
                    novel.artist = artist
                    novel.pending_artist_request = None
                    novel.save()
                
                return {'success': True, 'message': message}
                
        except Exception as e:
            return {'success': False, 'message': _('Có lỗi xảy ra khi duyệt yêu cầu.')}

    @staticmethod
    def reject_author_request(pk, rejected_reason):
        """Reject an author request"""
        if not rejected_reason.strip():
            return {'success': False, 'message': _('Vui lòng nhập lý do từ chối.')}
        
        author_request = get_object_or_404(AuthorRequest, pk=pk)
        author_request.approval_status = ApprovalStatus.REJECTED.value
        author_request.rejected_reason = rejected_reason
        author_request.save()
        
        return {'success': True, 'message': _('Yêu cầu thêm tác giả đã bị từ chối.')}

    @staticmethod
    def reject_artist_request(pk, rejected_reason):
        """Reject an artist request"""
        if not rejected_reason.strip():
            return {'success': False, 'message': _('Vui lòng nhập lý do từ chối.')}
        
        artist_request = get_object_or_404(ArtistRequest, pk=pk)
        artist_request.approval_status = ApprovalStatus.REJECTED.value
        artist_request.rejected_reason = rejected_reason
        artist_request.save()
        
        return {'success': True, 'message': _('Yêu cầu thêm họa sĩ đã bị từ chối.')}

