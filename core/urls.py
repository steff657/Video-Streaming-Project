from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_videos, name='search_videos'),
    path('upload/', views.upload_video, name='upload_video'),
    path('my-videos/', views.my_videos, name='my_videos'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
    path('video/<int:pk>/edit/', views.edit_video, name='edit_video'),
    path('video/<int:pk>/delete/', views.delete_video, name='delete_video'),
    path('video/<int:pk>/comment/', views.post_comment, name='post_comment'),
    path('video/<int:pk>/react/', views.react_video, name='react_video'),
    path(
        'comment/<int:pk>/delete/',
        views.delete_comment,
        name='delete_comment',
    ),
]
