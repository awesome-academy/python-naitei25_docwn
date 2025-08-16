from django import forms
from django.utils.translation import gettext_lazy as _
from novels.models import Tag
from django.utils.text import slugify

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'description']

    def clean_name(self):
        name = self.cleaned_data['name']
        slug = slugify(name)

        # Nếu đang chỉnh sửa (tức là self.instance đã có id)
        if Tag.objects.exclude(id=self.instance.id).filter(slug=slug).exists():
            raise forms.ValidationError(_("Tag với tên này đã tồn tại."))

        return name



    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.name)
        if commit:
            instance.save()
        return instance
