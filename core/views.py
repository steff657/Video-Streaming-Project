from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .forms import VideoUploadForm, VideoEditForm
from .models import Video, VideoReaction
from .forms import CommentForm
from .models import Comment
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.http import HttpResponseForbidden
from django.db.models import Count, Q


def index(request):
    query = request.GET.get('q', '').strip()
    queryset = Video.objects.select_related('owner')
    if request.user.is_authenticated:
        queryset = queryset.filter(
            Q(visibility=Video.Visibility.PUBLIC) | Q(owner=request.user)
        )
    else:
        queryset = queryset.filter(visibility=Video.Visibility.PUBLIC)

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(owner__username__icontains=query)
        )

    videos = queryset.order_by('-created_at')[:24]
    return render(
        request,
        'core/index.html',
        {'videos': videos, 'search_query': query},
    )


def search_videos(request):
    query = request.GET.get('q', '').strip()
    queryset = Video.objects.select_related('owner')

    if request.user.is_authenticated:
        queryset = queryset.filter(
            Q(visibility=Video.Visibility.PUBLIC) | Q(owner=request.user)
        )
    else:
        queryset = queryset.filter(visibility=Video.Visibility.PUBLIC)

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(owner__username__icontains=query)
        )

    videos = queryset.order_by('-created_at')[:24]
    html = render_to_string(
        'core/_video_grid.html',
        {'videos': videos},
        request=request,
    )
    return JsonResponse(
        {
            'success': True,
            'html': html,
            'count': videos.count(),
            'query': query,
        }
    )


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
    videos = (
        Video.objects.filter(owner=request.user)
        .select_related('owner')
        .order_by('-created_at')
    )
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
    video = get_object_or_404(
        Video.objects.select_related('owner')
        .prefetch_related('comments', 'reactions'),
        pk=pk
    )
    # enforce private visibility
    if (
        video.visibility == Video.Visibility.PRIVATE
        and request.user != video.owner
    ):
        response = render(request, 'core/not_allowed.html')
        response.status_code = 403
        return response

    reaction_counts = video.reactions.aggregate(
        likes=Count('id', filter=Q(value=VideoReaction.Reaction.LIKE)),
        dislikes=Count(
            'id', filter=Q(value=VideoReaction.Reaction.DISLIKE)
        ),
    )
    user_reaction = None
    if request.user.is_authenticated:
        user_reaction = (
            video.reactions.filter(user=request.user)
            .values_list('value', flat=True)
            .first()
        )

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
            'like_count': reaction_counts['likes'],
            'dislike_count': reaction_counts['dislikes'],
            'user_reaction': user_reaction,
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


@login_required
@require_POST
def react_video(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if (
        video.visibility == Video.Visibility.PRIVATE
        and request.user != video.owner
    ):
        return HttpResponseForbidden()

    value = request.POST.get('value')
    if value not in (
        VideoReaction.Reaction.LIKE,
        VideoReaction.Reaction.DISLIKE,
    ):
        return JsonResponse({'success': False}, status=400)

    reaction, created = VideoReaction.objects.get_or_create(
        video=video, user=request.user, defaults={'value': value}
    )

    if not created:
        if reaction.value == value:
            reaction.delete()
            current = None
        else:
            reaction.value = value
            reaction.save(update_fields=['value'])
            current = value
    else:
        current = value

    reaction_counts = video.reactions.aggregate(
        likes=Count('id', filter=Q(value=VideoReaction.Reaction.LIKE)),
        dislikes=Count(
            'id', filter=Q(value=VideoReaction.Reaction.DISLIKE)
        ),
    )

    return JsonResponse(
        {
            'success': True,
            'likes': reaction_counts['likes'],
            'dislikes': reaction_counts['dislikes'],
            'current': current,
        }
    )
