from enum import Enum
from django.utils.translation import gettext_lazy as _


class UserRole(Enum):
    GUEST = "g"
    USER = "u"
    WEBSITE_ADMIN = "wa"
    SYSTEM_ADMIN = "sa"

    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]


class Gender(Enum):
    MALE = "m"
    FEMALE = "f"
    OTHER = "o"

    @classmethod
    def choices(cls):
        return [
            (cls.MALE.value, _("Nam")),
            (cls.FEMALE.value, _("Nữ")),
            (cls.OTHER.value, _("Khác")),
        ]


class ProgressStatus(Enum):
    ONGOING = "o"
    COMPLETED = "c"
    SUSPEND = "s"

    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]


class ApprovalStatus(Enum):
    DRAFT = "d"
    PENDING = "p"
    APPROVED = "a"
    REJECTED = "r"

    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]
    

class NotificationTypeChoices:
    COMMENT = 'COMMENT'
    REPLY = 'REPLY'
    REVIEW = 'REVIEW'
    LIKE = 'LIKE'
    REPORT = 'REPORT'
    SYSTEM = 'SYSTEM'
    
    CHOICES = (
        (COMMENT, _('Bình luận mới')),
        (REPLY, _('Trả lời bình luận')),
        (REVIEW, _('Đánh giá mới')),
        (LIKE, _('Thích bình luận')),
        (REPORT, _('Báo cáo')),
        (SYSTEM, _('Hệ thống')),
    )

class ReportReasonChoices:
    SPAM = 'SPAM'
    OFFENSIVE = 'OFFENSIVE'
    HARASSMENT = 'HARASSMENT'
    FAKE = 'FAKE'
    COPYRIGHT = 'COPYRIGHT'
    OTHER = 'OTHER'
    
    CHOICES = (
        (SPAM, _('Spam')),
        (OFFENSIVE, _('Nội dung không phù hợp')),
        (HARASSMENT, _('Quấy rối')),
        (FAKE, _('Thông tin giả mạo')),
        (COPYRIGHT, _('Vi phạm bản quyền')),
        (OTHER, _('Khác')),
    )

class ReportStatusChoices:
    PENDING = 'PENDING'
    RESOLVED = 'RESOLVED'
    
    CHOICES = (
        (PENDING, _('Chờ xử lý')),
        (RESOLVED, _('Đã xử lý')),
    )

class RequestStatusChoices:
    PENDING = 'PENDING'
    PROCESSED = 'PROCESSED'
    
    CHOICES = (
        (PENDING, _('Chờ xử lý')),
        (PROCESSED, _('Đã xử lý')),
    )

class RequestSortChoices:
    CREATED_DESC = '-created_at'
    CREATED_ASC = 'created_at'
    TITLE_ASC = 'title'
    TITLE_DESC = '-title'
    STATUS_ASC = 'status'
    STATUS_DESC = '-status'
    USER_ASC = 'user__username'
    USER_DESC = '-user__username'
    
    CHOICES = (
        (CREATED_DESC, _('Ngày tạo (mới nhất)')),
        (CREATED_ASC, _('Ngày tạo (cũ nhất)')),
        (TITLE_ASC, _('Tiêu đề (A-Z)')),
        (TITLE_DESC, _('Tiêu đề (Z-A)')),
        (STATUS_ASC, _('Trạng thái (chờ xử lý trước)')),
        (STATUS_DESC, _('Trạng thái (đã xử lý trước)')),
        (USER_ASC, _('Người gửi (A-Z)')),
        (USER_DESC, _('Người gửi (Z-A)')),
    )

START_POSITION_DEFAULT = 1
PROGRESS_DEFAULT = 0.0
COUNT_DEFAULT = 0
LIMIT_DEFAULT = 5
OFFSET_DEFAULT = 0
DEFAULT_TIMEOUT = 5.0

# Constants for max_length
MAX_USERNAME_LENGTH = 255
MAX_EMAIL_LENGTH = 255
MAX_PASSWORD_LENGTH = 255
MAX_NAME_LENGTH = 255
MAX_TAG_LENGTH = 255
MAX_COUNTRY_LENGTH = 100
MAX_IMAGE_URL_LENGTH = 255
MAX_TITLE_LENGTH = 255
MAX_SLUG_LENGTH = 255  # For chapter slugs combining volume and title
MAX_TYPE_LENGTH = 255
MAX_GENDER_LENGTH = 1
MAX_STATUS_LENGTH = 1
MAX_ROLE_LENGTH = 2
MAX_REASON_LENGTH = 20
MAX_REPORT_STATUS_LENGTH = 20
MAX_REQUEST_STATUS_LENGTH = 20
MAX_REQUEST_TITLE_LENGTH = 255
MAX_SESSION_REMEMBER = 1209600
MAX_RATE = 5
MAX_TOKEN_LENGTH = 255
MAX_LIMIT_CHUNKS = 5
MAX_LIKE_NOVELS =18
MAX_TREND_NOVELS =30
MAX_MOST_READ_NOVELS =12
MAX_NEW_NOVELS = 100
MAX_NEW_NOVELS_ROW = 16
MAX_FINISH_NOVELS =13
MAX_NEWUPDATE_NOVELS =12
MAX_LATEST_CHAPTER = 12
MIN_LATEST_CHAPTER = 1
MAX_HOME_COMMENTS = 10  # Maximum comments to show on home page
MAX_RANDOM_STRING_LENGTH = 10
MAX_SESSION_REMEMBER = 2592000  # 30 days
MAX_TIME_RETRY_CONNECTION = 30
MAX_QUEUE_SIZE = 1000
MAX_IMAGE_SIZE = 16 * 1024 * 1024  # 16MB
MAX_IMAGE_SIZE_MB = 16  # 16MB
MAX_LIKE_NOVELS_PAGE = 8
MAX_LENGTH_REVIEW_CONTENT = 2000

# Constants for min_length
MIN_RATE = 0
MIN_PASSWORD_LENGTH = 8
MIN_TEXTAREA_ROWS = 3
MIN_SESSION_REMEMBER = 3600 # 1 hour
MIN_LIKE_COUNT = 0


# Date
DATE_FORMAT_DMY = "d/m/Y"
DATE_FORMAT_DMYHI = "d/m/Y H:i"
DATE_FORMAT_DMY2 = "%d/%m/%Y"
# Chapter
MAX_CHAPTER_LIST = 4
MAX_CHAPTER_LIST_PLUS = 5

# Novel validation
MIN_NOVEL_NAME_LENGTH = 3
MIN_NOVEL_SUMMARY_LENGTH = 10
MAX_NOVEL_SUMMARY_LENGTH = 2000
MAX_NOVEL_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# PAGINATOR
PAGINATOR_TAG_LIST = 10  # Increased for better consistency
PAGINATOR_COMMENT_LIST = 7
PAGINATOR_COMMON_LIST = 10  # Increased for better consistency
PAGINATOR_REVIEW_LIST = 10
PAGINATOR_REQUEST_LIST = 10  # For user requests
PAGINATOR_ADMIN_REQUEST_LIST = 20  # For admin requests
DEFAULT_PAGE_NUMBER = 1

# Allowed image types for novel uploads
ALLOWED_IMAGE_TYPES = [
    "image/jpeg",
    "image/jpg", 
    "image/png",
    "image/gif",
    "image/webp",
]

MAX_TRUNCATED_REJECTED_REASON_LENGTH = 10
MAX_REJECTTED_REASONS_LENGTH = 1000

# Constants for pagination
NOVEL_PER_PAGE = 10
PAGINATION_PAGE_RANGE = 3  # Number of pages to show before and after current page
PAGINATION_TEMPLATE_PATH = 'admin/includes/pagination_range.html'  # Template path for pagination
PAGINATION_MIN_PAGE = 1  # Minimum page number
PAGINATION_ELLIPSIS_THRESHOLD = 2  # Page difference threshold for showing ellipsis
PAGINATION_MIN_PAGES_TO_SHOW = 1  # Minimum number of pages required to show pagination

# Chunking configuration
MAX_CHUNK_SIZE = 10000  # Maximum size for a chunk in characters

# HTML Chunker constants
HTML_TAG_OVERHEAD = 20  # Buffer size for HTML tags like <p></p>
BEAUTIFULSOUP_PARSER = 'html.parser'
HTML_BLOCK_ELEMENTS = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

# Reading constants
WORDS_PER_MINUTE = 200  # Average reading speed for time estimation
SUMMARY_TRUNCATE_WORDS = 20  # Number of words to show in novel summary previews

# Draft constants
DEFAULT_DRAFT_NAME_PREFIX = "Draft"
DEFAULT_DRAFT_FALLBACK_NAME = "Novel"
DEFAULT_DRAFT_SUMMARY = "Draft content - to be updated later"

# Volume constants
MAX_VOLUME_NAME_LENGTH = 255

#Rating constants
DEFAULT_RATING_AVERAGE = 0.0

# Security constants
SECURE_HSTS_SECONDS_HEROKU = 31536000  # 1 year in seconds
SECURE_HSTS_SECONDS_DEVELOPMENT = 0  # No HSTS in development mode

# Time constants for relative time calculation
SECONDS_PER_HOUR = 3600  # 60 * 60
SECONDS_PER_MINUTE = 60
SEARCH_RESULTS_LIMIT = 20  # Limit for search results
COMMENT_TRUNCATE_LENGTH = 200  # Length to truncate comments

# Constants for attempting
MAX_ATTEMPTS = 10

# TinyMCE Editor constants
TINYMCE_HEIGHT = 400
TINYMCE_FONT_SIZE = 14
TINYMCE_COLS = 80
TINYMCE_ROWS = 20

# Textarea
TEXTAREA_ROWS = 3
MAX_COMMENT_LENGTH = 1000
