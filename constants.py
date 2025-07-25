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
