from django import forms
from django.utils.translation import gettext_lazy as _
from novels.models import AuthorRequest
from constants import (
    Gender,
    MIN_TEXTAREA_ROWS,
    MIN_PERSON_NAME_LENGTH,
)

class AuthorRequestForm(forms.ModelForm):
    class Meta:
        model = AuthorRequest
        fields = ['name', 'pen_name', 'description', 'birthday',
                   'deathday', 'gender', 'country']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Tên thật của tác giả'),
                'required': True,
            }),
            'pen_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Bút danh (nếu có)'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': MIN_TEXTAREA_ROWS,
                'placeholder': _('Mô tả về tác giả (tiểu sử, thành tựu, v.v.)'),
            }),
            'birthday': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'deathday': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control',
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Quốc gia'),
            }),
        }
        labels = {
            'name': _('Tên tác giả *'),
            'pen_name': _('Bút danh'),
            'description': _('Mô tả'),
            'birthday': _('Ngày sinh'),
            'deathday': _('Ngày mất'),
            'gender': _('Giới tính'),
            'country': _('Quốc gia'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add gender choices with empty option
        gender_choices = [('', _('--- Chọn giới tính ---'))] + Gender.choices()
        self.fields['gender'].choices = gender_choices
        self.fields['gender'].required = False

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            name = name.strip()
            if len(name) < MIN_PERSON_NAME_LENGTH:
                raise forms.ValidationError(_('Tên tác giả phải ' \
                'có ít nhất 2 ký tự.'))
            
            # Check if author already exists
            from novels.models import Author
            if Author.objects.filter(name=name).exists():
                raise forms.ValidationError(
                    _('Tác giả "{}" đã tồn tại trong hệ thống. Vui lòng chọn ' \
                    'tác giả có sẵn hoặc sử dụng tên khác.').format(name)
                )
        return name

    def clean_deathday(self):
        birthday = self.cleaned_data.get('birthday')
        deathday = self.cleaned_data.get('deathday')
        
        if birthday and deathday and deathday <= birthday:
            raise forms.ValidationError(_('Ngày mất phải sau ngày sinh.'))
        
        return deathday
