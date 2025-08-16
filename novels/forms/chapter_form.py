from django import forms
from django.utils.translation import gettext_lazy as _
from novels.models import Chapter, Volume
from django.utils.text import slugify
from novels.utils import ChunkManager, SimpleChunker
from constants import (
    MAX_VOLUME_NAME_LENGTH,
    MAX_CHUNK_SIZE,
)

class ChapterForm(forms.ModelForm):
    """Form for adding new chapters"""
    
    # Choice field for selecting existing volume or creating new one
    volume_choice = forms.ChoiceField(
        choices=[],  # Will be populated in __init__
        required=False,
        label=_("Chọn Volume"),
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )
    
    # Field for creating new volume
    new_volume_name = forms.CharField(
        max_length=MAX_VOLUME_NAME_LENGTH,
        required=False,
        label=_("Tên Volume mới"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Nhập tên volume mới..."),
            }
        ),
        help_text=_("Chap mới sẽ được thêm vào volume mới này")
    )
    
    # Chapter content field
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 15,
                "placeholder": _("Nhập nội dung chapter...")
            }
        ),
        label=_("Nội dung"),
    )

    class Meta:
        model = Chapter
        fields = ['title']
        widgets = {
            'title': forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Nhập tiêu đề chapter..."),
                }
            ),
        }
        labels = {
            'title': _("Tiêu đề Chapter"),
        }

    def __init__(self, novel=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.novel = novel
        
        if novel:
            # Get existing volumes for this novel
            volumes = Volume.objects.filter(novel=novel).order_by('position')
            volume_choices = [('', _('-- Chọn Volume --'))]
            volume_choices.extend([(vol.id, vol.name) for vol in volumes])
            volume_choices.append(('new', _('Tạo Volume mới')))
            
            self.fields['volume_choice'].choices = volume_choices

    def clean_new_volume_name(self):
        new_volume_name = self.cleaned_data.get('new_volume_name')
        volume_choice = self.cleaned_data.get('volume_choice')
        
        if volume_choice == 'new' and new_volume_name and self.novel:
            # Check if volume name already exists in this novel
            if Volume.objects.filter(novel=self.novel, name=new_volume_name).exists():
                raise forms.ValidationError(_("Tên volume đã tồn tại trong tiểu thuyết này"))
        
        return new_volume_name

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise forms.ValidationError(_("Tiêu đề chapter là bắt buộc"))
        return title.strip()

    def clean(self):
        cleaned_data = super().clean()
        volume_choice = cleaned_data.get('volume_choice')
        new_volume_name = cleaned_data.get('new_volume_name')
        title = cleaned_data.get('title')
        
        if not volume_choice:
            raise forms.ValidationError(_("Vui lòng chọn volume hoặc tạo volume mới"))
        
        if volume_choice == 'new' and not new_volume_name:
            raise forms.ValidationError(_("Vui lòng nhập tên volume mới"))
        
        if volume_choice != 'new' and volume_choice and new_volume_name:
            raise forms.ValidationError(_("Không thể vừa chọn volume có sẵn vừa tạo volume mới"))
        
        # Check for duplicate volume name when creating new volume
        if volume_choice == 'new' and new_volume_name and self.novel:
            if Volume.objects.filter(novel=self.novel, name=new_volume_name).exists():
                raise forms.ValidationError(_("Tên volume đã tồn tại trong tiểu thuyết này"))
        
        # Check for duplicate chapter title within the selected volume
        if title and self.novel:
            if volume_choice == 'new' and new_volume_name:
                # For new volume, check if the combination of volume name + chapter title
                # would create a duplicate slug
                volume_slug = slugify(new_volume_name)
                chapter_slug = slugify(title)
                
                # Check if any existing chapter would have the same slug pattern
                existing_chapters = Chapter.objects.filter(
                    volume__novel=self.novel,
                    deleted_at__isnull=True
                )
                
                for existing_chapter in existing_chapters:
                    existing_volume_slug = slugify(existing_chapter.volume.name)
                    existing_chapter_slug = slugify(existing_chapter.title)
                    
                    if (existing_volume_slug == volume_slug and 
                        existing_chapter_slug == chapter_slug):
                        raise forms.ValidationError(
                            _("Kết hợp tên volume và tiêu đề chapter này sẽ tạo ra slug trùng lặp")
                        )
                        
            elif volume_choice and volume_choice != 'new':
                # For existing volume, check within that specific volume
                try:
                    volume = Volume.objects.get(id=volume_choice, novel=self.novel)
                    existing_chapters = Chapter.objects.filter(
                        volume=volume,
                        title=title,
                        deleted_at__isnull=True
                    )
                    if existing_chapters.exists():
                        raise forms.ValidationError(_("Tiêu đề chapter đã tồn tại trong volume này"))
                except Volume.DoesNotExist:
                    raise forms.ValidationError(_("Volume được chọn không hợp lệ"))
            
        return cleaned_data

    def save(self, commit=True):
        chapter = super().save(commit=False)
        
        if not self.novel:
            raise ValueError("Novel must be provided")
            
        volume_choice = self.cleaned_data.get('volume_choice')
        new_volume_name = self.cleaned_data.get('new_volume_name')
        content = self.cleaned_data.get('content')
        
        # Handle volume selection or creation
        if volume_choice == 'new':
            # Create new volume
            last_volume = Volume.objects.filter(novel=self.novel).order_by('-position').first()
            next_position = (last_volume.position + 1) if last_volume else 1
            
            volume = Volume.objects.create(
                novel=self.novel,
                name=new_volume_name,
                position=next_position
            )
        else:
            # Use existing volume
            volume = Volume.objects.get(id=volume_choice, novel=self.novel)
        
        chapter.volume = volume
        
        # Set chapter position
        last_chapter = Chapter.objects.filter(volume=volume).order_by('-position').first()
        chapter.position = (last_chapter.position + 1) if last_chapter else 1
        
        # Note: slug will be generated automatically by the model's save method
        # which includes volume information to prevent conflicts
        
        if commit:
            chapter.save()
            
            # Use normal chunking to create chunks
            # Create simple chunker with database limit
            chunker = SimpleChunker(max_chunk_size=MAX_CHUNK_SIZE)  # Database TEXT field limit
            
            # Create chunks using normal chunking
            chunk_count = ChunkManager.create_normal_chunks_for_chapter(
                chapter=chapter,
                content=content,
                chunker=chunker
            )
            
            # Note: chapter.word_count is updated automatically by ChunkManager
        
        return chapter
