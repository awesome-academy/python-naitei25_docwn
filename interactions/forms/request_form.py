from django import forms
from django.utils.translation import gettext_lazy as _
from interactions.models import Request
from constants import MAX_REQUEST_TITLE_LENGTH


class RequestForm(forms.ModelForm):
    """Form để người dùng gửi yêu cầu/phản hồi"""
    
    class Meta:
        model = Request
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Nhập tiêu đề yêu cầu'),
                'maxlength': MAX_REQUEST_TITLE_LENGTH
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Mô tả chi tiết yêu cầu của bạn'),
                'rows': 6
            }),
        }
        labels = {
            'title': _('Tiêu đề'),
            'content': _('Nội dung'),
        }
        help_texts = {
            'title': _('Tóm tắt ngắn gọn về yêu cầu của bạn'),
            'content': _('Mô tả chi tiết vấn đề hoặc yêu cầu của bạn'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Đặt required cho tất cả các trường
        for field in self.fields.values():
            field.required = True

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 5:
                raise forms.ValidationError(_('Tiêu đề phải có ít nhất 5 ký tự.'))
        return title

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if content:
            content = content.strip()
            if len(content) < 10:
                raise forms.ValidationError(_('Nội dung phải có ít nhất 10 ký tự.'))
        return content


class AdminRequestProcessForm(forms.ModelForm):
    """Form để admin xử lý yêu cầu"""
    
    class Meta:
        model = Request
        fields = ['admin_note']
        widgets = {
            'admin_note': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Ghi chú phản hồi cho người dùng (tùy chọn)'),
                'rows': 4
            }),
        }
        labels = {
            'admin_note': _('Ghi chú admin'),
        }
        help_texts = {
            'admin_note': _('Phản hồi hoặc ghi chú cho người dùng (tùy chọn)'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['admin_note'].required = False
