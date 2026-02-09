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


class CommentForm(forms.Form):
    comment_text = forms.CharField(
        widget=forms.Textarea(
            attrs={
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
