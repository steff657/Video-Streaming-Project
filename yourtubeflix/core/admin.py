from django.contrib import admin
from .models import Video, Comment, VideoReaction


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'visibility', 'created_at')
    list_filter = ('visibility', 'created_at')
    search_fields = ('title', 'description', 'owner__username')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'video', 'user', 'created_at', 'is_deleted')
    list_filter = ('is_deleted', 'created_at')
    search_fields = ('comment_text', 'user__username', 'video__title')


@admin.register(VideoReaction)
class VideoReactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'video', 'user', 'value', 'created_at')
    list_filter = ('value', 'created_at')
    search_fields = ('user__username', 'video__title')
