from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_videos, name='search_videos'),
    path('upload/', views.upload_video, name='upload_video'),
    path('my-videos/', views.my_videos, name='my_videos'),
    path('me/profile/', views.edit_profile, name='edit_profile'),
    path('me/account/', views.account_settings, name='account_settings'),
    path('u/<str:username>/', views.profile_detail, name='profile_detail'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
    path('video/<int:pk>/edit/', views.edit_video, name='edit_video'),
    path('video/<int:pk>/delete/', views.delete_video, name='delete_video'),
    path('video/<int:pk>/comment/', views.post_comment, name='post_comment'),
    path('video/<int:pk>/react/', views.react_video, name='react_video'),
    path('video/<int:pk>/report/', views.report_video, name='report_video'),
    path(
        'comment/<int:pk>/delete/',
        views.delete_comment,
        name='delete_comment',
    ),
    path(
        'comment/<int:pk>/edit/',
        views.edit_comment,
        name='edit_comment',
    ),
    path(
        'staff/users/',
        views.admin_user_management,
        name='admin_user_management',
    ),
    path(
        'staff/users/<int:user_id>/delete/',
        views.admin_delete_user,
        name='admin_delete_user',
    ),
    path('staff/reports/', views.admin_reports, name='admin_reports'),
    path(
        'staff/reports/<int:report_id>/resolve/',
        views.admin_resolve_report,
        name='admin_resolve_report',
    ),
    path(
        'staff/reports/<int:report_id>/delete-video/',
        views.admin_delete_reported_video,
        name='admin_delete_reported_video',
    ),
]
