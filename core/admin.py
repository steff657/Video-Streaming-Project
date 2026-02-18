from django.contrib import admin
from .models import (
    AdminActionLog,
    Comment,
    Profile,
    Report,
    Video,
    VideoReaction,
)


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


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'display_name', 'updated_at')
    search_fields = ('user__username', 'display_name')
    readonly_fields = ('updated_at',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reporter', 'video', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('reporter__username', 'video__title', 'reason')
    readonly_fields = ('created_at', 'resolved_at')


@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'action', 'admin_user', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = (
        'admin_user__username',
        'target_user__username',
        'target_video__title',
    )
    readonly_fields = ('created_at',)
