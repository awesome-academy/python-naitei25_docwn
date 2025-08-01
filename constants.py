from enum import Enum


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
        return [(i.value, i.name) for i in cls]


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

START_POSITION_DEFAULT = 1
PROGRESS_DEFAULT = 0.0
COUNT_DEFAULT = 0

# Constants for max_length
MAX_USERNAME_LENGTH = 255
MAX_EMAIL_LENGTH = 255
MAX_PASSWORD_LENGTH = 255
MAX_NAME_LENGTH = 255
MAX_TAG_LENGTH = 255
MAX_COUNTRY_LENGTH = 100
MAX_IMAGE_URL_LENGTH = 255
MAX_TITLE_LENGTH = 255
MAX_TYPE_LENGTH = 255
MAX_GENDER_LENGTH = 1
MAX_STATUS_LENGTH = 1
MAX_ROLE_LENGTH = 2
MAX_SESSION_REMEMBER = 1209600
MAX_RATE = 5
MAX_TOKEN_LENGTH = 255
MAX_LIMIT_CHUNKS = 5

# Constants for min_length
MIN_RATE = 0
MIN_PASSWORD_LENGTH = 8
MIN_TEXTAREA_ROWS = 3
MIN_SESSION_REMEMBER = 0

# Session
SESSION_COOKIE_AGE_SECONDS = 86400  # 24 hours

# Date
DATE_FORMAT_DMY = "d/m/Y"
DATE_FORMAT_DMYHI = "d/m/Y H:i"

# Chapter
MAX_CHAPTER_LIST = 4
MAX_CHAPTER_LIST_PLUS = 5

# Novel validation
MIN_NOVEL_NAME_LENGTH = 3
MIN_NOVEL_SUMMARY_LENGTH = 10
MAX_NOVEL_SUMMARY_LENGTH = 2000
MAX_NOVEL_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# PAGINATOR
PAGINATOR_TAG_LIST = 5
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
