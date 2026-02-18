from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.core.files import File as DjangoFile
from django.contrib.auth import get_user_model
import subprocess
import os
import uuid
from pathlib import Path as FilePath
from django.utils import timezone
from .video_processing import generate_thumbnail_from_video
import tempfile
import json


def validate_file_size(file):
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 200 * 1024 * 1024)
    if file.size > max_size:
        raise ValidationError(
            _('File too large. Maximum size is %(max)s bytes.'),
            params={'max': max_size},
        )


def validate_video_resolution(file):
    max_width = getattr(settings, 'MAX_VIDEO_WIDTH', 3840)
    max_height = getattr(settings, 'MAX_VIDEO_HEIGHT', 2160)
    temp_path = None
    probe_path = None

    try:
        if hasattr(file, 'temporary_file_path'):
            probe_path = file.temporary_file_path()
        else:
            suffix = FilePath(getattr(file, 'name', '')).suffix or '.tmp'
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
            ) as tmp:
                for chunk in file.chunks():
                    tmp.write(chunk)
                temp_path = tmp.name
            probe_path = temp_path
            file.seek(0)

        cmd = [
            'ffprobe',
            '-v',
            'error',
            '-select_streams',
            'v:0',
            '-show_entries',
            'stream=width,height',
            '-of',
            'json',
            probe_path,
        ]
        completed = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        data = json.loads(completed.stdout or '{}')
        streams = data.get('streams') or []
        if not streams:
            return

        width = streams[0].get('width')
        height = streams[0].get('height')
        if (
            isinstance(width, int)
            and isinstance(height, int)
            and (width > max_width or height > max_height)
        ):
            raise ValidationError(
                _(
                    'Video resolution too high. Maximum allowed is '
                    '%(max_width)dx%(max_height)d.'
                ),
                params={
                    'max_width': max_width,
                    'max_height': max_height,
                },
            )
    except FileNotFoundError:
        # ffprobe unavailable in runtime; skip resolution validation.
        return
    except subprocess.CalledProcessError:
        # Probe failure should not block uploads.
        return
    finally:
        if temp_path:
            try:
                os.remove(temp_path)
            except OSError:
                pass


class Video(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = 'public', _('Public')
        PRIVATE = 'private', _('Private')
        UNLISTED = 'unlisted', _('Unlisted')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='videos',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    tags = models.JSONField(blank=True, default=list)
    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )
    video_file = models.FileField(
        upload_to='videos/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=getattr(
                    settings,
                    'ALLOWED_VIDEO_EXTENSIONS',
                    ['mp4', 'mov', 'webm', 'mkv'],
                )
            ),
            validate_file_size,
            validate_video_resolution,
        ],
    )
    thumbnail = models.ImageField(
        upload_to='thumbnails/', null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.owner})"

    @property
    def content_type(self):
        ext = FilePath(self.video_file.name).suffix.lower()
        mime_map = {
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.webm': 'video/webm',
            '.mkv': 'video/x-matroska',
            '.m4v': 'video/x-m4v',
            '.avi': 'video/x-msvideo',
            '.wmv': 'video/x-ms-wmv',
            '.flv': 'video/x-flv',
            '.mpg': 'video/mpeg',
            '.mpeg': 'video/mpeg',
            '.3gp': 'video/3gpp',
            '.ogv': 'video/ogg',
            '.ts': 'video/mp2t',
            '.m2ts': 'video/mp2t',
        }
        return mime_map.get(ext, 'application/octet-stream')

    def generate_thumbnail(self, time='00:00:01'):
        """Generate a thumbnail using ffmpeg if available.

        Requires `ffmpeg` to be on the system PATH. If ffmpeg is missing or
        the operation fails, this function will silently return.
        """
        if not self.video_file:
            return

        try:
            input_path = self.video_file.path
        except Exception:
            return

        thumb_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
        output_path = generate_thumbnail_from_video(
            input_path=input_path,
            output_dir=thumb_dir,
            time=time,
        )
        if not output_path:
            return
        filename = os.path.basename(output_path)

        # Save generated thumbnail into the ImageField
        try:
            with open(output_path, 'rb') as f:
                django_file = DjangoFile(f)
                # use save=False to avoid recursion
                self.thumbnail.save(filename, django_file, save=False)
        finally:
            try:
                os.remove(output_path)
            except OSError:
                pass

    def transcode_to_mp4(self):
        """Transcode uploaded video to MP4 (H.264 video + AAC audio)."""
        if not self.video_file:
            return False

        try:
            input_path = self.video_file.path
        except Exception:
            return False

        if not os.path.exists(input_path):
            return False

        output_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
        os.makedirs(output_dir, exist_ok=True)
        temp_output_name = f"{uuid.uuid4().hex}.mp4"
        temp_output_path = os.path.join(output_dir, temp_output_name)

        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-movflags', '+faststart',
            temp_output_path,
        ]

        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception:
            try:
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
            except OSError:
                pass
            return False

        old_name = self.video_file.name
        stem = FilePath(old_name).stem or 'video'
        final_name = f"{stem}-{uuid.uuid4().hex[:8]}.mp4"

        try:
            with open(temp_output_path, 'rb') as f:
                self.video_file.save(final_name, DjangoFile(f), save=False)
        finally:
            try:
                os.remove(temp_output_path)
            except OSError:
                pass

        if old_name != self.video_file.name:
            try:
                self.video_file.storage.delete(old_name)
            except Exception:
                pass
        return True

    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        can_change_video_file = (
            update_fields is None or 'video_file' in update_fields
        )
        video_file_changed = False
        if self.video_file and can_change_video_file:
            if self.pk:
                previous = (
                    Video.objects.filter(pk=self.pk)
                    .only('video_file')
                    .first()
                )
                video_file_changed = (
                    previous is None
                    or previous.video_file.name != self.video_file.name
                )
            else:
                video_file_changed = True

        # Ensure the instance is saved first so `video_file.path` exists
        super().save(*args, **kwargs)

        # Normalize uploads to MP4/H.264/AAC only on new or changed file uploads
        if video_file_changed and self.transcode_to_mp4():
            super().save(update_fields=['video_file'])

        # Generate thumbnail if missing
        if not self.thumbnail and self.video_file:
            self.generate_thumbnail()
            # Save again if thumbnail was set
            super().save(update_fields=['thumbnail'])

    def delete(self, *args, **kwargs):
        storage = self.video_file.storage
        # capture names before deletion
        video_name = self.video_file.name
        thumb_name = self.thumbnail.name if self.thumbnail else None
        super().delete(*args, **kwargs)
        # remove files from storage
        try:
            if video_name:
                storage.delete(video_name)
        except Exception:
            pass
        try:
            if thumb_name:
                storage.delete(thumb_name)
        except Exception:
            pass


class Comment(models.Model):
    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Comment {self.pk} by {self.user} on {self.video}"

    def soft_delete(self):
        if not self.is_deleted:
            self.is_deleted = True
            self.comment_text = ''
            self.deleted_at = timezone.now()
            self.save(
                update_fields=['is_deleted', 'comment_text', 'deleted_at']
            )


class VideoReaction(models.Model):
    class Reaction(models.TextChoices):
        LIKE = 'like', _('Like')
        DISLIKE = 'dislike', _('Dislike')

    video = models.ForeignKey(
        Video, on_delete=models.CASCADE, related_name='reactions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='video_reactions',
    )
    value = models.CharField(max_length=10, choices=Reaction.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['video', 'user'], name='unique_video_reaction'
            )
        ]

    def __str__(self):
        return f"{self.user} {self.value} {self.video}"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    display_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to='profiles/', null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

    @property
    def effective_display_name(self):
        return self.display_name.strip() or self.user.username


class Report(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        RESOLVED = 'resolved', _('Resolved')

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_reports',
    )
    video = models.ForeignKey(
        Video,
        on_delete=models.SET_NULL,
        related_name='reports',
        null=True,
        blank=True,
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_reports',
    )

    def __str__(self):
        target = f"video:{self.video_id}" if self.video_id else "unknown"
        return f"Report {self.pk} by {self.reporter_id} ({target})"

    def resolve(self, by_user):
        self.status = self.Status.RESOLVED
        self.resolved_by = by_user
        self.resolved_at = timezone.now()
        self.save(update_fields=['status', 'resolved_by', 'resolved_at'])


class AdminActionLog(models.Model):
    class Action(models.TextChoices):
        DELETE_VIDEO = 'delete_video', _('Delete Video')
        DELETE_USER = 'delete_user', _('Delete User')
        RESOLVE_REPORT = 'resolve_report', _('Resolve Report')

    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_action_logs',
    )
    action = models.CharField(max_length=50, choices=Action.choices)
    target_user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    target_video = models.ForeignKey(
        Video,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    target_report = models.ForeignKey(
        Report,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    details = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} by {self.admin_user_id} at {self.created_at}"

