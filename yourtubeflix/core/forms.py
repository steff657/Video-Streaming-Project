from django import forms
from .models import Video


class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'tags', 'visibility', 'video_file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class VideoEditForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'tags', 'visibility']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
