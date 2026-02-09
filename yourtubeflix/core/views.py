from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .forms import VideoUploadForm, VideoEditForm
from .models import Video
from .forms import CommentForm
from .models import Comment
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden


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
            return JsonResponse(
                {'success': True, 'video_id': video.id}
            )
        return JsonResponse(
            {'success': False, 'errors': form.errors}, status=400
        )

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
    return render(
        request, 'core/edit_video.html', {'form': form, 'video': video}
    )


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
    if (
        video.visibility == Video.Visibility.PRIVATE
        and request.user != video.owner
    ):
        return render(request, 'core/not_allowed.html', status=403)

    # comments and comment form
    comments = video.comments.order_by('-created_at')[:100]
    form = CommentForm()
    return render(
        request,
        'core/video_detail.html',
        {
            'video': video,
            'comments': comments,
            'comment_form': form,
        },
    )


@login_required
@require_POST
def post_comment(request, pk):
    video = get_object_or_404(Video, pk=pk)
    form = CommentForm(request.POST)
    if not form.is_valid():
        return JsonResponse(
            {'success': False, 'errors': form.errors}, status=400
        )

    comment = Comment.objects.create(
        video=video,
        user=request.user,
        comment_text=form.cleaned_data['comment_text'],
    )

    html = render_to_string(
        'core/_comment.html', {'comment': comment, 'user': request.user}
    )
    return JsonResponse(
        {'success': True, 'html': html, 'comment_id': comment.id}
    )


@login_required
@require_POST
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user:
        return HttpResponseForbidden()
    comment.soft_delete()
    return JsonResponse({'success': True, 'comment_id': comment.id})
