from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _


def validate_file_size(file):
	max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 200 * 1024 * 1024)
	if file.size > max_size:
		raise ValidationError(
			from django.conf import settings
			from django.db import models
			from django.core.exceptions import ValidationError
			from django.core.validators import FileExtensionValidator
			from django.utils.translation import gettext_lazy as _
			from django.core.files import File as DjangoFile
			import subprocess
			import os
			import uuid


			def validate_file_size(file):
				max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 200 * 1024 * 1024)
				if file.size > max_size:
					raise ValidationError(
						_('File too large. Maximum size is %(max)s bytes.'),
						params={'max': max_size},
					)


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
					],
				)
				thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
				created_at = models.DateTimeField(auto_now_add=True)

				def __str__(self):
					return f"{self.title} ({self.owner})"

				def generate_thumbnail(self, time='00:00:01'):
					"""Attempt to generate a thumbnail using ffmpeg. Requires ffmpeg in PATH.

					This method is safe to call but will silently return if ffmpeg is not available.
					"""
					if not self.video_file:
						return

					try:
						input_path = self.video_file.path
					except Exception:
						return

					thumb_dir = os.path.join(settings.MEDIA_ROOT, 'thumbnails')
					os.makedirs(thumb_dir, exist_ok=True)
					filename = f"{uuid.uuid4().hex}.jpg"
					output_path = os.path.join(thumb_dir, filename)

					cmd = [
						'ffmpeg', '-y', '-ss', time, '-i', input_path,
						'-vframes', '1', '-q:v', '2', output_path,
					]

					try:
						subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
					except Exception:
						# ffmpeg not available or failed; do nothing
						return

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

				def save(self, *args, **kwargs):
					# If new instance (no PK) or no thumbnail, save first to ensure file path
					is_new = self.pk is None
					super().save(*args, **kwargs)

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

