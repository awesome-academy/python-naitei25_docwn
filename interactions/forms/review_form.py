from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from interactions.models import Review
from constants import (
    MIN_RATE, MAX_RATE,
    MAX_LENGTH_REVIEW_CONTENT
)


class ReviewForm(forms.ModelForm):
    """Form cho việc tạo và chỉnh sửa đánh giá"""
    
    rating = forms.IntegerField(
        validators=[MinValueValidator(MIN_RATE + 1), MaxValueValidator(MAX_RATE)],
        widget=forms.Select(choices=[(i, f"{i} sao") for i in range(MIN_RATE + 1, MAX_RATE + 1)]),
        label=_("Đánh giá"),
        help_text=_(f"Đánh giá từ {MIN_RATE + 1}-{MAX_RATE} sao")
    )
    
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': _('Chia sẻ cảm nhận của bạn về cuốn tiểu thuyết này...'),
            'class': 'form-control bg-body text-body'
        }),
        label=_("Nội dung đánh giá"),
        max_length=MAX_LENGTH_REVIEW_CONTENT,
        help_text=_(f"Tối đa {MAX_LENGTH_REVIEW_CONTENT} ký tự")
    )

    class Meta:
        model = Review
        fields = ['rating', 'content']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.novel = kwargs.pop('novel', None)
        super().__init__(*args, **kwargs)
        
        # Thêm CSS classes
        for field_name, field in self.fields.items():
            if field_name == 'rating':
                field.widget.attrs.update({'class': 'form-select bg-body text-body rating-select'})
            elif field_name == 'content':
                field.widget.attrs.update({'class': 'form-control bg-body text-body'})

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise forms.ValidationError(_("Nội dung đánh giá không được để trống."))
        return content

    def save(self, commit=True):
        review = super().save(commit=False)
        if self.user:
            review.user = self.user
        if self.novel:
            review.novel = self.novel
        if commit:
            review.save()
        return review


class ReviewDeleteForm(forms.Form):
    """Form xác nhận xóa đánh giá"""
    confirm = forms.BooleanField(
        required=True,
        label=_("Tôi xác nhận muốn xóa đánh giá này"),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input bg-body text-body'})
    )
