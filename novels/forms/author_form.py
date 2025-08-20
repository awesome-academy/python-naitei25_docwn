from django import forms
from novels.models import Author
from django.utils.translation import gettext_lazy as _
from constants import Gender

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'pen_name', 'description', 'birthday', 'deathday', 'gender', 'country', 'image_url']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Tên thật của tác giả'),
            }),
            'pen_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Bút danh (nếu có)'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
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
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('URL hình ảnh'),
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
            'image_url': _('Hình ảnh'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gender'].choices = [('', _('--- Chọn giới tính ---'))] + Gender.choices()

    def clean_name(self):
        name = self.cleaned_data['name']

        # Nếu đang chỉnh sửa (tức là self.instance đã có id)
        if Author.objects.exclude(id=self.instance.id).filter(name=name).exists(): 
            raise forms.ValidationError(_("Tác giả này đã tồn tại."))

        return name

    def clean_deathday(self):
        birthday = self.cleaned_data.get('birthday')
        deathday = self.cleaned_data.get('deathday')
        
        if birthday and deathday and deathday <= birthday:
            raise forms.ValidationError(_("Ngày mất phải sau ngày sinh."))
        
        return deathday
