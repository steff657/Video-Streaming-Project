from django import forms
from .models import Video


class VideoUploadForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Comma-separated tags',
            }
        ),
    )

    class Meta:
        model = Video
        fields = ['title', 'description', 'tags', 'visibility', 'video_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter video title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter video description',
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-select',
            }),
            'video_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*',
            }),
        }

    def clean_tags(self):
        raw_tags = self.cleaned_data.get('tags', '')
        if not raw_tags:
            return []
        return [
            tag.strip()
            for tag in raw_tags.split(',')
            if tag.strip()
        ]


class VideoEditForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Comma-separated tags',
            }
        ),
    )

    class Meta:
        model = Video
        fields = ['title', 'description', 'tags', 'visibility']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter video title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter video description',
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.tags:
            self.fields['tags'].initial = ', '.join(self.instance.tags)

    def clean_tags(self):
        raw_tags = self.cleaned_data.get('tags', '')
        if not raw_tags:
            return []
        return [
            tag.strip()
            for tag in raw_tags.split(',')
            if tag.strip()
        ]


class CommentForm(forms.Form):
    comment_text = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Add a comment...',
            }
        ),
        required=True,
        max_length=2000,
    )

    def clean_comment_text(self):
        text = self.cleaned_data.get('comment_text', '')
        if not text or not text.strip():
            raise forms.ValidationError('Comment cannot be empty.')
        return text.strip()
