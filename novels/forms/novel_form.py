from django import forms
from django.utils.translation import gettext_lazy as _
from django_select2.forms import Select2MultipleWidget, Select2Widget
from novels.models import Novel, Tag, Author, Artist, AuthorRequest, ArtistRequest
from constants import (
    MIN_NOVEL_NAME_LENGTH,
    MIN_NOVEL_SUMMARY_LENGTH,
    MAX_NOVEL_SUMMARY_LENGTH,
    MAX_NOVEL_IMAGE_SIZE,
    ALLOWED_IMAGE_TYPES,
    DEFAULT_DRAFT_NAME_PREFIX,
    DEFAULT_DRAFT_FALLBACK_NAME,
    DEFAULT_DRAFT_SUMMARY,
    ProgressStatus,
    ApprovalStatus,
)
from common.utils import ExternalAPIManager

class NovelForm(forms.ModelForm):

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=Select2MultipleWidget(
            attrs={
                "data-placeholder": _("Chọn thể loại..."),
                "data-label": _("Thể loại"),
            }
        ),
        required=False,
        label=_("Thể loại"),
        help_text=_("Chọn một hoặc nhiều thể loại cho tiểu thuyết"),
    )

    author = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=False,
        label=_("Tác giả"),
        widget=forms.Select(
            attrs={
                "data-placeholder": _("Chọn tác giả..."),
                "data-label": _("Tác giả"),
                "class": "form-control",
            }
        ),
    )

    artist = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=False,
        label=_("Họa sĩ"),
        widget=forms.Select(
            attrs={
                "data-placeholder": _("Chọn họa sĩ..."),
                "data-label": _("Họa sĩ"),
                "class": "form-control",
            }
        ),
    )

    upload_anonymously = forms.BooleanField(
        required=False,
        initial=False,
        label=_("Đăng ẩn danh"),
        help_text=_(
            "Chọn để đăng tiểu thuyết mà không hiển thị tên người đăng"
        ),
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
                "data-label": _("Đăng ẩn danh"),
                "data-placeholder": _("Chọn để đăng ẩn danh"),
            }
        ),
    )

    image_file = forms.ImageField(
        required=False,
        label=_("Ảnh bìa"),
        help_text=_("Tải lên ảnh bìa cho tiểu thuyết"),
        widget=forms.FileInput(
            attrs={
                "accept": "image/*",
                "data-label": _("Ảnh bìa"),
                "data-placeholder": _("Chọn ảnh bìa..."),
                "data-upload-text": _("Chọn ảnh từ thiết bị của bạn"),
                "data-preview-text": _("Xem trước ảnh"),
            }
        ),
    )

    progress_status = forms.ChoiceField(
        choices=[
            (ProgressStatus.ONGOING.value, _("ĐANG TIẾN HÀNH")),
            (ProgressStatus.COMPLETED.value, _("HOÀN THÀNH")),
            (ProgressStatus.SUSPEND.value, _("TẠM DỪNG")),
        ],
        required=False,
        label=_("Trạng thái tiến độ"),
        widget=forms.Select(
            attrs={
                "data-placeholder": _("Chọn trạng thái..."),
                "data-label": _("Trạng thái tiến độ"),
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = Novel
        fields = ["name", "other_names", "summary"]
        labels = {
            "name": _("Tên tiểu thuyết"),
            "other_names": _("Tên khác"),
            "summary": _("Tóm tắt"),
        }
        help_texts = {
            "summary": _(
                "Viết tóm tắt ngắn gọn về nội dung tiểu thuyết "
                "(tối thiểu {min} ký tự, tối đa {max} ký tự)"
            ).format(
                min=MIN_NOVEL_SUMMARY_LENGTH, max=MAX_NOVEL_SUMMARY_LENGTH
            ),
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": _("Nhập tên tiểu thuyết"),
                    "data-placeholder": _("Nhập tên tiểu thuyết"),
                    "data-label": _("Tên tiểu thuyết"),
                    "data-required-msg": _("Tên tiểu thuyết là bắt buộc"),
                    "data-min-length-msg": _(
                        "Tên tiểu thuyết phải có ít nhất {min} ký tự"
                    ).format(min=MIN_NOVEL_NAME_LENGTH),
                }
            ),
            "other_names": forms.TextInput(
                attrs={
                    "placeholder": _("Nhập tên khác (tùy chọn)"),
                    "data-placeholder": _("Nhập tên khác (tùy chọn)"),
                    "data-label": _("Tên khác"),
                }
            ),
            "summary": forms.Textarea(
                attrs={
                    "placeholder": _("Nhập tóm tắt nội dung tiểu thuyết"),
                    "data-placeholder": _("Nhập tóm tắt nội dung tiểu thuyết"),
                    "data-label": _("Tóm tắt"),
                    "data-required-msg": _("Tóm tắt là bắt buộc"),
                    "data-min-length-msg": _(
                        "Tóm tắt phải có ít nhất {min} ký tự"
                    ).format(min=MIN_NOVEL_SUMMARY_LENGTH),
                    "data-max-length": str(MAX_NOVEL_SUMMARY_LENGTH),
                    "data-counter-template": _("{current}/{max} ký tự"),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Check if user already exists as author/artist
        user_is_existing_author = False
        user_is_existing_artist = False

        if self.user:
            user_name = self.user.get_name()
            user_is_existing_author = Author.objects.filter(
                name=user_name
            ).exists()
            user_is_existing_artist = Artist.objects.filter(
                name=user_name
            ).exists()

        # Populate author choices
        author_choices = [
            ("", _("--- Chọn tác giả ---")),
            ("unknown", _("Không rõ")),
        ]

        # Only add "Me" option if user is not already an author
        if self.user and not user_is_existing_author:
            author_choices.append(("me", _("Tôi")))

        # Add existing authors (including user if they are already an author)
        for author in Author.objects.all():
            author_choices.append((f"author_{author.id}", author.name))

        # Add user's pending/approved author requests
        if self.user:
            user_author_requests = AuthorRequest.objects.filter(
                created_by=self.user,
                approval_status__in=[ApprovalStatus.PENDING.value, ApprovalStatus.APPROVED.value]
            ).order_by('-created_at')
            
            for request in user_author_requests:
                status_label = _("(Chờ duyệt)") if request.approval_status == ApprovalStatus.PENDING.value else _("(Đã duyệt)")
                display_name = f"{request.get_display_name()} {status_label}"
                author_choices.append((f"author_request_{request.id}", display_name))

        # Add option to create new author request
        if self.user:
            author_choices.append(("create_new_author", _("+ Tạo yêu cầu thêm tác giả mới")))

        self.fields["author"].choices = author_choices

        # Populate artist choices
        artist_choices = [
            ("", _("--- Chọn họa sĩ ---")),
            ("unknown", _("Không rõ")),
        ]

        # Only add "Me" option if user is not already an artist
        if self.user and not user_is_existing_artist:
            artist_choices.append(("me", _("Tôi")))

        # Add existing artists (including user if they are already an artist)
        for artist in Artist.objects.all():
            artist_choices.append((f"artist_{artist.id}", artist.name))

        # Add user's pending/approved artist requests
        if self.user:
            user_artist_requests = ArtistRequest.objects.filter(
                created_by=self.user,
                approval_status__in=[ApprovalStatus.PENDING.value, ApprovalStatus.APPROVED.value]
            ).order_by('-created_at')
            
            for request in user_artist_requests:
                status_label = _("(Chờ duyệt)") if request.approval_status == ApprovalStatus.PENDING.value else _("(Đã duyệt)")
                display_name = f"{request.get_display_name()} {status_label}"
                artist_choices.append((f"artist_request_{request.id}", display_name))

        # Add option to create new artist request
        if self.user:
            artist_choices.append(("create_new_artist", _("+ Tạo yêu cầu thêm họa sĩ mới")))

        self.fields["artist"].choices = artist_choices

    def clean(self):
        cleaned_data = super().clean()

        # Check if this is a draft save (less strict validation)
        is_draft = (
            hasattr(self, "request")
            and self.request
            and self.request.POST.get("save_as_draft", False)
        )

        if not is_draft:
            # Full validation for non-draft submissions
            name = cleaned_data.get("name")
            summary = cleaned_data.get("summary")

            if not name or not name.strip():
                raise forms.ValidationError(
                    _("Tên tiểu thuyết là bắt buộc khi xuất bản.")
                )

            if not summary or not summary.strip():
                raise forms.ValidationError(
                    _("Tóm tắt là bắt buộc khi xuất bản.")
                )

            if len(name.strip()) < MIN_NOVEL_NAME_LENGTH:
                raise forms.ValidationError(
                    _("Tên tiểu thuyết phải có ít nhất {min} ký tự.").format(
                        min=MIN_NOVEL_NAME_LENGTH
                    )
                )

            if len(summary.strip()) < MIN_NOVEL_SUMMARY_LENGTH:
                raise forms.ValidationError(
                    _("Tóm tắt phải có ít nhất {min} ký tự.").format(
                        min=MIN_NOVEL_SUMMARY_LENGTH
                    )
                )

        return cleaned_data

    def clean_author(self):
        author = self.cleaned_data.get("author")
        # Allow empty, "unknown", "me", "create_new_author", or valid author IDs/requests
        if author and author not in ["", "unknown", "me", "create_new_author"]:
            if author.startswith("author_request_"):
                try:
                    request_id = int(author.replace("author_request_", ""))
                    if not AuthorRequest.objects.filter(
                        id=request_id,
                        created_by=self.user,
                        approval_status__in=[ApprovalStatus.PENDING.value, ApprovalStatus.APPROVED.value]
                    ).exists():
                        raise forms.ValidationError(_("Yêu cầu thêm tác giả được chọn không tồn tại hoặc không hợp lệ."))
                except ValueError:
                    raise forms.ValidationError(_("Lựa chọn tác giả không hợp lệ."))
            elif author.startswith("author_"):
                try:
                    author_id = int(author.replace("author_", ""))
                    if not Author.objects.filter(id=author_id).exists():
                        raise forms.ValidationError(_("Tác giả được chọn không tồn tại."))
                except ValueError:
                    raise forms.ValidationError(_("Lựa chọn tác giả không hợp lệ."))
            else:
                raise forms.ValidationError(_("Lựa chọn tác giả không hợp lệ."))
        return author

    def clean_artist(self):
        artist = self.cleaned_data.get("artist")
        # Allow empty, "unknown", "me", "create_new_artist", or valid artist IDs/requests
        if artist and artist not in ["", "unknown", "me", "create_new_artist"]:
            if artist.startswith("artist_request_"):
                try:
                    request_id = int(artist.replace("artist_request_", ""))
                    if not ArtistRequest.objects.filter(
                        id=request_id,
                        created_by=self.user,
                        approval_status__in=[ApprovalStatus.PENDING.value, ApprovalStatus.APPROVED.value]
                    ).exists():
                        raise forms.ValidationError(_("yêu cầu thêm họa sĩ được chọn không tồn tại hoặc không hợp lệ."))
                except ValueError:
                    raise forms.ValidationError(_("Lựa chọn họa sĩ không hợp lệ."))
            elif artist.startswith("artist_"):
                try:
                    artist_id = int(artist.replace("artist_", ""))
                    if not Artist.objects.filter(id=artist_id).exists():
                        raise forms.ValidationError(_("Họa sĩ được chọn không tồn tại."))
                except ValueError:
                    raise forms.ValidationError(_("Lựa chọn họa sĩ không hợp lệ."))
            else:
                raise forms.ValidationError(_("Lựa chọn họa sĩ không hợp lệ."))
        return artist

    def clean_image_file(self):
        image = self.cleaned_data.get("image_file")
        if image:
            # Check file size
            if image.size > MAX_NOVEL_IMAGE_SIZE:
                max_size_mb = MAX_NOVEL_IMAGE_SIZE // (1024 * 1024)
                raise forms.ValidationError(
                    _("Kích thước file phải nhỏ hơn {max}MB.").format(
                        max=max_size_mb
                    )
                )

            # Check file type
            if image.content_type not in ALLOWED_IMAGE_TYPES:
                raise forms.ValidationError(
                    _("Chỉ chấp nhận file ảnh (JPEG, PNG, GIF, WebP).")
                )

        return image

    def upload_to_imgbb(self, image):
        """Upload image using external API manager"""
        return ExternalAPIManager.upload_image(image)

    def save(self, commit=True):
        novel = super().save(commit=False)
        
        # Check if this is a draft save
        is_draft = (
            hasattr(self, "request")
            and self.request
            and self.request.POST.get("save_as_draft", False)
        )
        
        # Handle empty name for drafts
        if is_draft and (not novel.name or not novel.name.strip()):
            novel.name = f"{DEFAULT_DRAFT_NAME_PREFIX} {self.user.get_name() if self.user else DEFAULT_DRAFT_FALLBACK_NAME}"
            
        # Handle empty summary for drafts
        if is_draft and (not novel.summary or not novel.summary.strip()):
            novel.summary = DEFAULT_DRAFT_SUMMARY
            
        # Set progress status if not provided
        progress_status = self.cleaned_data.get("progress_status")
        if progress_status:
            novel.progress_status = progress_status
        else:
            # Set default progress status from constants
            novel.progress_status = ProgressStatus.ONGOING.value

        # Handle author selection
        author_choice = self.cleaned_data.get("author")
        if not author_choice or author_choice == "unknown":
            # Empty choice or Unknown author -> set to null
            novel.author = None
            novel.pending_author_request = None
        elif author_choice == "me" and self.user:
            # Create or get Author record for the user
            author, created = Author.objects.get_or_create(
                name=self.user.get_name(),
                defaults={"description": f"Tác giả: {self.user.get_name()}"},
            )
            novel.author = author
            novel.pending_author_request = None
        elif author_choice and author_choice.startswith("author_request_"):
            # Author request selected
            request_id = author_choice.replace("author_request_", "")
            try:
                author_request = AuthorRequest.objects.get(id=int(request_id))
                if author_request.approval_status == ApprovalStatus.APPROVED.value and author_request.created_author:
                    # Use the approved author
                    novel.author = author_request.created_author
                    novel.pending_author_request = None
                else:
                    # Use the pending request
                    novel.author = None
                    novel.pending_author_request = author_request
            except (AuthorRequest.DoesNotExist, ValueError):
                novel.author = None
                novel.pending_author_request = None
        elif author_choice and author_choice.startswith("author_"):
            # Existing author selected
            author_id = author_choice.replace("author_", "")
            try:
                author = Author.objects.get(id=int(author_id))
                novel.author = author
                novel.pending_author_request = None
            except (Author.DoesNotExist, ValueError):
                novel.author = None
                novel.pending_author_request = None

        # Handle artist selection
        artist_choice = self.cleaned_data.get("artist")
        if not artist_choice or artist_choice == "unknown":
            # Empty choice or Unknown artist -> set to null
            novel.artist = None
            novel.pending_artist_request = None
        elif artist_choice == "me" and self.user:
            # Create or get Artist record for the user
            artist, created = Artist.objects.get_or_create(
                name=self.user.get_name(),
                defaults={"description": f"Họa sĩ: {self.user.get_name()}"},
            )
            novel.artist = artist
            novel.pending_artist_request = None
        elif artist_choice and artist_choice.startswith("artist_request_"):
            # Artist request selected
            request_id = artist_choice.replace("artist_request_", "")
            try:
                artist_request = ArtistRequest.objects.get(id=int(request_id))
                if artist_request.approval_status == ApprovalStatus.APPROVED.value and artist_request.created_artist:
                    # Use the approved artist
                    novel.artist = artist_request.created_artist
                    novel.pending_artist_request = None
                else:
                    # Use the pending request
                    novel.artist = None
                    novel.pending_artist_request = artist_request
            except (ArtistRequest.DoesNotExist, ValueError):
                novel.artist = None
                novel.pending_artist_request = None
        elif artist_choice and artist_choice.startswith("artist_"):
            # Existing artist selected
            artist_id = artist_choice.replace("artist_", "")
            try:
                artist = Artist.objects.get(id=int(artist_id))
                novel.artist = artist
                novel.pending_artist_request = None
            except (Artist.DoesNotExist, ValueError):
                novel.artist = None
                novel.pending_artist_request = None

        # Handle image upload
        image = self.cleaned_data.get("image_file")
        if image:
            image_url = self.upload_to_imgbb(image)
            if image_url:
                novel.image_url = image_url
            # If upload fails, continue without image

        if commit:
            novel.save()
            self.save_m2m()
        return novel

