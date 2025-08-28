from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta

from interactions.models import Request
from constants import RequestStatusChoices, RequestSortChoices


class RequestService:
    """Service layer để xử lý logic business của Request"""

    @staticmethod
    def create_request(user, title, content):
        """Tạo yêu cầu mới từ người dùng"""
        try:
            request = Request.objects.create(
                user=user,
                title=title.strip(),
                content=content.strip(),
                status=RequestStatusChoices.PENDING
            )
            return {
                'success': True,
                'request': request,
                'message': _('Yêu cầu của bạn đã được gửi thành công. Chúng tôi sẽ xem xét và phản hồi sớm nhất có thể.')
            }
        except Exception as e:
            return {
                'success': False,
                'message': _('Có lỗi xảy ra khi gửi yêu cầu. Vui lòng thử lại.')
            }

    @staticmethod
    def get_user_requests(user, page=1, per_page=10, status_filter=None, sort_by=None, search=None):
        """Lấy danh sách yêu cầu của người dùng với phân trang, lọc và sắp xếp"""
        try:
            requests = Request.objects.filter(user=user)
            
            # Apply filters
            if status_filter:
                requests = requests.filter(status=status_filter)
            
            if search:
                requests = requests.filter(
                    Q(title__icontains=search) | Q(content__icontains=search)
                )
            
            # Apply sorting
            if sort_by and sort_by in [choice[0] for choice in RequestSortChoices.CHOICES]:
                requests = requests.order_by(sort_by)
            else:
                requests = requests.order_by('-created_at')
            
            paginator = Paginator(requests, per_page)
            
            try:
                requests_page = paginator.page(page)
            except PageNotAnInteger:
                requests_page = paginator.page(1)
            except EmptyPage:
                requests_page = paginator.page(paginator.num_pages)
            
            return {
                'success': True,
                'requests': requests_page,
                'total_count': paginator.count
            }
        except Exception as e:
            return {
                'success': False,
                'message': _('Có lỗi xảy ra khi tải danh sách yêu cầu.')
            }

    @staticmethod
    def get_all_requests_for_admin(page=1, per_page=20, status_filter=None, sort_by=None, 
                                   search=None, date_from=None, date_to=None, user_filter=None):
        """Lấy tất cả yêu cầu cho admin với phân trang, lọc và sắp xếp nâng cao"""
        try:
            requests = Request.objects.select_related('user', 'processed_by')
            
            # Apply filters
            if status_filter:
                requests = requests.filter(status=status_filter)
            
            if search:
                requests = requests.filter(
                    Q(title__icontains=search) | 
                    Q(content__icontains=search) |
                    Q(user__username__icontains=search) |
                    Q(user__email__icontains=search)
                )
            
            if date_from:
                try:
                    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                    start_of_day = timezone.make_aware(
                        datetime.combine(date_from_obj, datetime.min.time())
                    )
                    requests = requests.filter(created_at__gte=start_of_day)
                except ValueError:
                    pass
            
            if date_to:
                try:
                    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                    end_of_day = timezone.make_aware(
                        datetime.combine(date_to_obj, datetime.max.time())
                    )
                    requests = requests.filter(created_at__lte=end_of_day)
                except ValueError:
                    pass
            
            if user_filter:
                requests = requests.filter(
                    Q(user__username__icontains=user_filter) |
                    Q(user__email__icontains=user_filter)
                )
            
            # Apply sorting
            if sort_by and sort_by in [choice[0] for choice in RequestSortChoices.CHOICES]:
                requests = requests.order_by(sort_by)
            else:
                requests = requests.order_by('-created_at')
            
            paginator = Paginator(requests, per_page)
            
            try:
                requests_page = paginator.page(page)
            except PageNotAnInteger:
                requests_page = paginator.page(1)
            except EmptyPage:
                requests_page = paginator.page(paginator.num_pages)
            
            return {
                'success': True,
                'requests': requests_page,
                'total_count': paginator.count
            }
        except Exception as e:
            return {
                'success': False,
                'message': _('Có lỗi xảy ra khi tải danh sách yêu cầu.')
            }

    @staticmethod
    def get_request_detail(request_id, user=None):
        """Lấy chi tiết yêu cầu"""
        try:
            request_obj = Request.objects.select_related('user', 'processed_by').get(id=request_id)
            
            # Kiểm tra quyền truy cập
            if user and not user.is_staff and request_obj.user != user:
                return {
                    'success': False,
                    'message': _('Bạn không có quyền xem yêu cầu này.')
                }
            
            return {
                'success': True,
                'request': request_obj
            }
        except Request.DoesNotExist:
            return {
                'success': False,
                'message': _('Không tìm thấy yêu cầu.')
            }
        except Exception as e:
            return {
                'success': False,
                'message': _('Có lỗi xảy ra khi tải chi tiết yêu cầu.')
            }

    @staticmethod
    def process_request(request_id, admin_user, admin_note=""):
        """Xử lý yêu cầu bởi admin"""
        try:
            request_obj = Request.objects.get(id=request_id)
            
            if request_obj.is_processed:
                return {
                    'success': False,
                    'message': _('Yêu cầu này đã được xử lý trước đó.')
                }
            
            request_obj.mark_processed(admin_user, admin_note.strip())
            
            return {
                'success': True,
                'request': request_obj,
                'message': _('Đã đánh dấu yêu cầu là đã xử lý.')
            }
        except Request.DoesNotExist:
            return {
                'success': False,
                'message': _('Không tìm thấy yêu cầu.')
            }
        except Exception as e:
            return {
                'success': False,
                'message': _('Có lỗi xảy ra khi xử lý yêu cầu.')
            }

    @staticmethod
    def get_request_statistics():
        """Lấy thống kê yêu cầu"""
        try:
            today = timezone.now().date()
            
            total_count = Request.objects.count()
            pending_count = Request.objects.filter(status=RequestStatusChoices.PENDING).count()
            processed_count = Request.objects.filter(status=RequestStatusChoices.PROCESSED).count()
            today_count = Request.objects.filter(created_at__date=today).count()
            
            return {
                'success': True,
                'statistics': {
                    'total_count': total_count,
                    'pending_count': pending_count,
                    'processed_count': processed_count,
                    'today_count': today_count,
                }
            }
        except Exception as e:
            return {
                'success': False,
                'message': _('Có lỗi xảy ra khi tải thống kê.')
            }
