from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .forms import VideoUploadForm, VideoEditForm
from .models import Video


def index(request):
    return render(request, 'core/index.html')


@login_required
def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.owner = request.user
            video.save()
            return JsonResponse({'success': True, 'video_id': video.id})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = VideoUploadForm()
    return render(request, 'core/upload.html', {'form': form})


@login_required
def my_videos(request):
    videos = Video.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'core/my_videos.html', {'videos': videos})


@login_required
def edit_video(request, pk):
    video = get_object_or_404(Video, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = VideoEditForm(request.POST, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, 'Video updated.')
            return redirect('my_videos')
    else:
        form = VideoEditForm(instance=video)
    return render(request, 'core/edit_video.html', {'form': form, 'video': video})


@login_required
def delete_video(request, pk):
    video = get_object_or_404(Video, pk=pk, owner=request.user)
    if request.method == 'POST':
        video.delete()
        messages.success(request, 'Video deleted.')
        return redirect('my_videos')
    return render(request, 'core/delete_confirm.html', {'video': video})


def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    # enforce private visibility
    if video.visibility == Video.Visibility.PRIVATE and request.user != video.owner:
        return render(request, 'core/not_allowed.html', status=403)
    return render(request, 'core/video_detail.html', {'video': video})
