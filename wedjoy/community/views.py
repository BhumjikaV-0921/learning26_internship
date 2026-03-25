from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Post, Comment
from .forms import PostForm, CommentForm

@login_required
def community_feed(request):
    """Main community feed view"""
    posts = Post.objects.all().prefetch_related('comments__user', 'user')
    post_form = PostForm()

    if request.method == 'POST' and 'post_content' in request.POST:
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect('community:feed')

    return render(request, 'community/feed.html', {
        'posts': posts,
        'post_form': post_form
    })

@login_required
@require_POST
def add_comment(request, post_id):
    """Add comment to a post via AJAX"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.post = post
        comment.save()

        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'user': comment.user.firstName or comment.user.email,
                'created_at': comment.created_at.strftime('%b %d, %Y %H:%M')
            }
        })

    return JsonResponse({'success': False, 'errors': form.errors})

@login_required
def user_posts(request):
    """View user's own posts"""
    posts = Post.objects.filter(user=request.user).prefetch_related('comments__user')
    return render(request, 'community/user_posts.html', {'posts': posts})
