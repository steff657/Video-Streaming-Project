from django.contrib import admin
from .models import Video, Comment, VideoReaction


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'visibility', 'created_at')
    list_filter = ('visibility', 'created_at')
    search_fields = ('title', 'description', 'owner__username')
    readonly_fields = ('created_at', 'thumb_preview')

    def thumb_preview(self, obj):
        if obj.thumbnail:
            from django.utils.html import format_html
            return format_html(
                '<img src="{}" width="100" height="100" />',
                obj.thumbnail.url,
            )
        return "-"
    thumb_preview.short_description = 'Thumbnail Preview'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'video', 'user', 'created_at', 'is_deleted')
    list_filter = ('is_deleted', 'created_at')
    search_fields = ('comment_text', 'user__username', 'video__title')
    readonly_fields = ('created_at', 'deleted_at')


@admin.register(VideoReaction)
class VideoReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'video', 'user', 'value', 'created_at')
    list_filter = ('value', 'created_at')
    search_fields = ('user__username', 'video__title')
    readonly_fields = ('created_at',)
