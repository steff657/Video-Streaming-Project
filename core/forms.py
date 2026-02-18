from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Profile, Report, Video


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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['display_name', 'bio', 'profile_picture']
        widgets = {
            'display_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Display name'}
            ),
            'bio': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4}
            ),
            'profile_picture': forms.FileInput(
                attrs={'class': 'form-control', 'accept': 'image/*'}
            ),
        }


class AccountSettingsForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )
    current_password = forms.CharField(
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    new_password = forms.CharField(
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Leave blank to keep current password.',
    )
    confirm_new_password = forms.CharField(
        required=False,
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['email'].initial = self.user.email

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        User = get_user_model()
        if (
            User.objects.exclude(pk=self.user.pk)
            .filter(email__iexact=email)
            .exists()
        ):
            raise forms.ValidationError('That email is already in use.')
        return email

    def clean_current_password(self):
        password = self.cleaned_data['current_password']
        if not self.user.check_password(password):
            raise forms.ValidationError('Current password is incorrect.')
        return password

    def clean(self):
        cleaned = super().clean()
        new_password = cleaned.get('new_password')
        confirm = cleaned.get('confirm_new_password')
        if new_password or confirm:
            if new_password != confirm:
                self.add_error(
                    'confirm_new_password',
                    'New password and confirmation must match.',
                )
            if new_password:
                try:
                    validate_password(new_password, self.user)
                except DjangoValidationError as exc:
                    self.add_error('new_password', exc)
        return cleaned


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Describe the issue with this video',
                }
            )
        }

    def clean_reason(self):
        reason = self.cleaned_data.get('reason', '').strip()
        if not reason:
            raise forms.ValidationError('Report reason cannot be empty.')
        return reason
